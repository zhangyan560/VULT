"""
埋点 T+1 定时任务 — DataPilot SQL 生成器

与 gen_hive_sql.py 的差异（仅改平台适配层，列生成逻辑不变）：
  1. 所有 CREATE TABLE ... AS / DROP TABLE → INSERT OVERWRITE PARTITION(dt='{dt}')
  2. 写入表名不带库前缀（DataPilot 规范）
  3. 读取 base/feat_* 时增加 WHERE dt='{dt}' 分区过滤
  4. daily_cnt 不再做滑窗（单天写入，原 sliding → 单次 INSERT）
  5. 日期参数来自 DataPilot 变量 ${p_date_iso}，由平台在执行前替换

用法（由各 task 脚本调用，不直接执行）：
    from gen_hive_sql_datapilot import generate_sql
    sql = generate_sql(job="A", dt=dt)
    spark.sql(sql)
"""

from config_datapilot import (
    TABLE, MAX_LOOKBACK_DAYS, BASE_TABLE_RISK_TYPES,
    event_in_clause, PAIR_EVENTS, CROSS_RATIO_CONFIG,
    DIM_CONFIG, PAIR_CONFIG,
)

# ── 复用原始列生成函数（不依赖 TABLE，只生成 CASE WHEN 列表达式）──────────────
from gen_hive_sql import (
    _gen_dim1_cols, _gen_dim2_cols, _gen_dim3_cols, _gen_dim4_cols,
    _gen_dim5_simple_cols, _gen_dim5_streak_gap_cols, _gen_dim5_slope_cols,
    _gen_dim5_ewm_cols, _gen_dim5_active_gap_cols,
    _gen_dim6_cols,
    _collect_job_a_cols, _collect_job_b_cols,
    _collect_job_c_cols, _collect_job_d_cols,
    _pair_alias,
)


# ═══════════════════════════════════════════════════════════════
# Task 1: 人群 base 表
# ═══════════════════════════════════════════════════════════════

def sql_base_table(dt: str) -> str:
    """
    INSERT OVERWRITE base PARTITION(dt='{dt}')
    原 batch_date 列改为 dt 分区键，业务含义不变。
    读取 underwrite 的分区为 date_sub(dt, 1)（T-2），保持原逻辑。
    """
    return f"""
INSERT OVERWRITE TABLE {TABLE['base_write']}
    PARTITION(dt = '{dt}')
SELECT DISTINCT
    loan_account_id,
    user_id
FROM {TABLE['underwrite']}
WHERE from_unixtime(bigint(trace_created_ts/1000)-3600, 'yyyy-MM-dd') >= '2025-01-01'
  AND trace_risk_type_name IN ({BASE_TABLE_RISK_TYPES})
  AND dt = date_format(date_sub('{dt}', 1), 'yyyyMMdd');
"""


# ═══════════════════════════════════════════════════════════════
# Task 2: daily_cnt 单天写入
# ═══════════════════════════════════════════════════════════════

def sql_daily_cnt_insert(dt: str) -> str:
    """
    INSERT OVERWRITE daily_cnt PARTITION(event_date='{dt}')
    原脚本滑窗刷新3天；DataPilot 单任务只允许一个 INSERT，改为只写当天分区。
    历史补刷可手动重跑指定日期的任务。
    """
    return f"""
INSERT OVERWRITE TABLE {TABLE['daily_cnt_write']}
    PARTITION(event_date = '{dt}')
SELECT
    loan_account_id,
    event_code,
    CAST(COUNT(*) AS INT)                AS daily_cnt,
    COALESCE(SUM(event_duration), 0)     AS daily_dur_sum,
    COALESCE(MAX(event_duration), 0)     AS daily_dur_max
FROM {TABLE['event_log']}
WHERE dt = REGEXP_REPLACE('{dt}', '-', '')
  AND event_code IN {event_in_clause()}
  AND loan_account_id IS NOT NULL
GROUP BY loan_account_id, event_code;
"""


# ═══════════════════════════════════════════════════════════════
# Task 3: Job A — Dim 1-4 + Dim5 simple
# ═══════════════════════════════════════════════════════════════

def sql_job_a(dt: str) -> str:
    anchor = f"'{dt}'"
    all_cols = (
        _gen_dim1_cols()
        + _gen_dim2_cols()
        + _gen_dim3_cols()
        + _gen_dim4_cols()
        + _gen_dim5_simple_cols()
    )
    return f"""
INSERT OVERWRITE TABLE {TABLE['feat_a_write']}
    PARTITION(dt = '{dt}')
SELECT
    b.loan_account_id
{chr(10).join(all_cols)}
FROM {TABLE['base']} b
LEFT JOIN (
    SELECT loan_account_id, event_code, event_date, daily_cnt,
           daily_cnt * daily_cnt AS daily_cnt_sq,
           DATEDIFF({anchor}, event_date) AS days_back
    FROM {TABLE['daily_cnt']}
    WHERE event_date >= DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS})
      AND event_date < {anchor}
) d ON b.loan_account_id = d.loan_account_id
WHERE b.dt = '{dt}'
GROUP BY b.loan_account_id;
"""


# ═══════════════════════════════════════════════════════════════
# Task 4: Job B — Dim 5 complex (streak/gap/slope/ewm/active_gap)
# ═══════════════════════════════════════════════════════════════

def sql_job_b(dt: str) -> str:
    anchor = f"'{dt}'"
    all_cols = (
        _gen_dim5_streak_gap_cols()
        + _gen_dim5_slope_cols()
        + _gen_dim5_ewm_cols()
        + _gen_dim5_active_gap_cols()
    )
    return f"""
INSERT OVERWRITE TABLE {TABLE['feat_b_write']}
    PARTITION(dt = '{dt}')
WITH day_seq AS (
    SELECT
        d.loan_account_id,
        d.event_code,
        d.event_date,
        d.daily_cnt,
        DATEDIFF({anchor}, d.event_date) AS days_back,
        DATEDIFF(d.event_date,
            LAG(d.event_date) OVER (
                PARTITION BY d.loan_account_id, d.event_code ORDER BY d.event_date
            )) AS gap_days
    FROM {TABLE['daily_cnt']} d
    INNER JOIN {TABLE['base']} b
        ON d.loan_account_id = b.loan_account_id
        AND b.dt = '{dt}'
    WHERE d.event_date >= DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS})
      AND d.event_date < {anchor}
      AND d.daily_cnt > 0
),
streak_calc AS (
    SELECT
        loan_account_id,
        event_code,
        event_date,
        days_back,
        DATEDIFF(event_date, '1970-01-01') - ROW_NUMBER() OVER (
            PARTITION BY loan_account_id, event_code ORDER BY event_date
        ) AS streak_grp
    FROM day_seq
),
streak_len AS (
    SELECT
        loan_account_id,
        event_code,
        streak_grp,
        MIN(days_back)  AS streak_min_db,
        COUNT(*)        AS streak_length
    FROM streak_calc
    GROUP BY loan_account_id, event_code, streak_grp
)
SELECT
    COALESCE(sl.loan_account_id, ds.loan_account_id) AS loan_account_id
{chr(10).join(all_cols)}
FROM (SELECT DISTINCT loan_account_id FROM day_seq) uid
LEFT JOIN streak_len sl ON uid.loan_account_id = sl.loan_account_id
LEFT JOIN day_seq ds    ON uid.loan_account_id = ds.loan_account_id
GROUP BY COALESCE(sl.loan_account_id, ds.loan_account_id);
"""


# ═══════════════════════════════════════════════════════════════
# Task 5: Job C — Dim 6 时间间隔
# ═══════════════════════════════════════════════════════════════

def sql_job_c(dt: str) -> str:
    anchor = f"'{dt}'"
    dim6_cols = _gen_dim6_cols()
    return f"""
INSERT OVERWRITE TABLE {TABLE['feat_c_write']}
    PARTITION(dt = '{dt}')
WITH evt AS (
    SELECT
        e.loan_account_id,
        e.event_code,
        e.created_date,
        DATEDIFF({anchor}, TO_DATE(e.created_date)) AS days_back,
        LAG(e.created_date) OVER (
            PARTITION BY e.loan_account_id, e.event_code
            ORDER BY e.created_date
        ) AS prev_created_date
    FROM {TABLE['event_log']} e
    INNER JOIN {TABLE['base']} b
        ON e.loan_account_id = b.loan_account_id
        AND e.user_id = b.user_id
        AND b.dt = '{dt}'
    WHERE e.dt >= REGEXP_REPLACE(CAST(DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS + 1}) AS STRING), '-', '')
      AND e.event_code IN {event_in_clause()}
      AND e.loan_account_id IS NOT NULL
      AND TO_DATE(e.created_date) < {anchor}
),
itv AS (
    SELECT
        loan_account_id,
        event_code,
        days_back,
        (UNIX_TIMESTAMP(created_date) - UNIX_TIMESTAMP(prev_created_date)) / 3600.0 AS gap_hours
    FROM evt
    WHERE prev_created_date IS NOT NULL
)
SELECT
    loan_account_id
{chr(10).join(dim6_cols)}
FROM itv
GROUP BY loan_account_id;
"""


# ═══════════════════════════════════════════════════════════════
# Task 6: Job D — Dim 7 A→B 序列 + 跨事件比率（rate_chg 预留）
# ═══════════════════════════════════════════════════════════════

def sql_job_d(dt: str) -> str:
    anchor = f"'{dt}'"

    pair_ctes = []
    pair_select_parts = []

    for idx, (ev_a, ev_b, win_h, _label) in enumerate(PAIR_CONFIG):
        pname = f"p{idx}"
        pa = _pair_alias(ev_a, ev_b)
        win_sec = int(win_h * 3600)

        pair_ctes.append(f"""{pname} AS (
    SELECT
        a.loan_account_id,
        a.created_date AS a_time,
        MIN(CASE
            WHEN b.event_code = '{ev_b}'
             AND b.created_date > a.created_date
             AND (UNIX_TIMESTAMP(b.created_date) - UNIX_TIMESTAMP(a.created_date)) <= {win_sec}
            THEN b.created_date
        END) AS first_b_time
    FROM evt_filtered a
    LEFT JOIN evt_filtered b ON a.loan_account_id = b.loan_account_id
    WHERE a.event_code = '{ev_a}'
    GROUP BY a.loan_account_id, a.created_date
)""")

        pair_select_parts.append(f"""
    ,COUNT({pname}.a_time) AS {pa}_cnt_all
    ,SUM(CASE WHEN {pname}.first_b_time IS NOT NULL THEN 1 ELSE 0 END) * 1.0
        / NULLIF(COUNT({pname}.a_time), 0) AS {pa}_rate_all
    ,AVG(CASE WHEN {pname}.first_b_time IS NOT NULL
        THEN (UNIX_TIMESTAMP({pname}.first_b_time) - UNIX_TIMESTAMP({pname}.a_time)) / 3600.0 END)
        AS {pa}_time_avg_all
    ,MIN(CASE WHEN {pname}.first_b_time IS NOT NULL
        THEN (UNIX_TIMESTAMP({pname}.first_b_time) - UNIX_TIMESTAMP({pname}.a_time)) / 3600.0 END)
        AS {pa}_time_min_all
    ,NULL AS {pa}_rate_chg""")

    ctes_sql = ",\n".join(pair_ctes)
    selects_sql = "".join(pair_select_parts)
    left_joins = "\n".join(
        f"LEFT JOIN p{i} ON uid.loan_account_id = p{i}.loan_account_id"
        for i in range(len(PAIR_CONFIG))
    )

    return f"""
INSERT OVERWRITE TABLE {TABLE['feat_d_write']}
    PARTITION(dt = '{dt}')
WITH evt_filtered AS (
    SELECT
        e.loan_account_id,
        e.event_code,
        e.created_date
    FROM {TABLE['event_log']} e
    INNER JOIN {TABLE['base']} b
        ON e.loan_account_id = b.loan_account_id
        AND e.user_id = b.user_id
        AND b.dt = '{dt}'
    WHERE e.dt >= REGEXP_REPLACE(CAST(DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS + 1}) AS STRING), '-', '')
      AND e.event_code IN {event_in_clause(PAIR_EVENTS)}
      AND e.loan_account_id IS NOT NULL
      AND TO_DATE(e.created_date) < {anchor}
),
uid AS (
    SELECT DISTINCT loan_account_id FROM evt_filtered
),
{ctes_sql}
SELECT
    uid.loan_account_id
{selects_sql}
FROM uid
{left_joins}
GROUP BY uid.loan_account_id;
"""


# ═══════════════════════════════════════════════════════════════
# Task 7: Merge — 合并 feat_a/b/c/d + 跨事件比率 → features
# ═══════════════════════════════════════════════════════════════

def sql_merge(dt: str) -> str:
    a_cols = [f"    ,a.{c}" for c in _collect_job_a_cols()]
    b_cols = [f"    ,b.{c}" for c in _collect_job_b_cols()]
    c_cols = [f"    ,c.{c}" for c in _collect_job_c_cols()]
    d_cols = [f"    ,d.{c}" for c in _collect_job_d_cols()]
    cross_cols = [
        f"    ,a.{numerator} / {denominator} AS {name}"
        for name, numerator, denominator in CROSS_RATIO_CONFIG
    ]
    all_select = a_cols + b_cols + c_cols + d_cols + cross_cols

    return f"""
INSERT OVERWRITE TABLE {TABLE['features_write']}
    PARTITION(dt = '{dt}')
SELECT
    a.loan_account_id
{chr(10).join(all_select)}
FROM {TABLE['feat_a']} a
LEFT JOIN {TABLE['feat_b']} b
    ON a.loan_account_id = b.loan_account_id AND b.dt = '{dt}'
LEFT JOIN {TABLE['feat_c']} c
    ON a.loan_account_id = c.loan_account_id AND c.dt = '{dt}'
LEFT JOIN {TABLE['feat_d']} d
    ON a.loan_account_id = d.loan_account_id AND d.dt = '{dt}'
WHERE a.dt = '{dt}';
"""


# ═══════════════════════════════════════════════════════════════
# 统一入口
# ═══════════════════════════════════════════════════════════════

JOB_GENERATORS = {
    "base":      sql_base_table,
    "daily_cnt": sql_daily_cnt_insert,
    "A":         sql_job_a,
    "B":         sql_job_b,
    "C":         sql_job_c,
    "D":         sql_job_d,
    "merge":     sql_merge,
}


def generate_sql(job: str, dt: str) -> str:
    gen = JOB_GENERATORS.get(job)
    if gen is None:
        raise ValueError(f"Unknown job: {job}. Available: {list(JOB_GENERATORS.keys())}")
    return gen(dt)
