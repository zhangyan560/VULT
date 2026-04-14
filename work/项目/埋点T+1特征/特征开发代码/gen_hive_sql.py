"""
埋点 T+1 定时任务 — Hive SQL 代码生成器

用法：
    python3 gen_hive_sql.py --mode t1   --job all   --dt 2026-04-08 --output sql/
    python3 gen_hive_sql.py --mode hist --job A      --output sql/
    python3 gen_hive_sql.py --mode t1   --job A,B    --dt 2026-04-08 --output sql/

生成的 SQL 按 Job 拆分写入 --output 目录。
"""

import argparse
import os
from datetime import datetime, timedelta
from config import (
    TABLE, EVENT_CONFIG, ALL_EVENTS, WINDOWS, WINDOWS_WITH_ALL, ALL_WINDOW,
    MAX_LOOKBACK_DAYS, DIM_CONFIG, PAIR_CONFIG, PAIR_EVENTS,
    CROSS_RATIO_CONFIG, BASE_TABLE_RISK_TYPES,
    event_in_clause, window_cond, feat_name,
)


# ═══════════════════════════════════════════════════════════════
# 通用 SQL 片段
# ═══════════════════════════════════════════════════════════════

def sql_base_table(dt: str) -> str:
    """Stage 0: 构建人群 base 表（T+1 模式）"""
    return f"""
DROP TABLE IF EXISTS {TABLE['base']};
CREATE TABLE {TABLE['base']} STORED AS PARQUET AS
SELECT DISTINCT
    loan_account_id,
    user_id,
    '{dt}' AS batch_date
FROM {TABLE['underwrite']}
WHERE from_unixtime(bigint(trace_created_ts/1000)-3600, 'yyyy-MM-dd') >= '2025-01-01'
  AND trace_risk_type_name IN ({BASE_TABLE_RISK_TYPES})
  AND dt = date_format(date_sub('{dt}', 1), 'yyyyMMdd');
"""


def sql_daily_cnt_insert(dt: str, refresh_date: str) -> str:
    """Stage 1: daily_cnt 单天 INSERT OVERWRITE"""
    return f"""
INSERT OVERWRITE TABLE {TABLE['daily_cnt']}
    PARTITION(event_date = '{refresh_date}')
SELECT
    loan_account_id,
    event_code,
    CAST(COUNT(*) AS INT)                     AS daily_cnt,
    COALESCE(SUM(event_duration), 0)          AS daily_dur_sum,
    COALESCE(MAX(event_duration), 0)          AS daily_dur_max
FROM {TABLE['event_log']}
WHERE dt = REGEXP_REPLACE('{refresh_date}', '-', '')
  AND event_code IN {event_in_clause()}
  AND loan_account_id IS NOT NULL
GROUP BY loan_account_id, event_code;
"""


def sql_daily_cnt_sliding(dt: str, n_days: int = 3) -> str:
    """Stage 1: 滑窗刷新最近 n_days 天，用 Python 计算具体日期"""
    dt_obj = datetime.strptime(dt, "%Y-%m-%d")
    parts = []
    for i in range(1, n_days + 1):
        refresh = (dt_obj - timedelta(days=i)).strftime("%Y-%m-%d")
        parts.append(sql_daily_cnt_insert(dt, refresh))
    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════
# Job A: Dim 1-4 + Dim 5 simple
# ═══════════════════════════════════════════════════════════════

def _gen_dim1_cols():
    """Dim 1: cnt / days / ever / max_daily × 7 windows × 65 events"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in WINDOWS_WITH_ALL:
            wc = window_cond("d.days_back", w)
            cols.append(
                f"    ,COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} "
                f"THEN d.daily_cnt ELSE 0 END), 0) AS {feat_name(a, 'cnt', w)}"
            )
            cols.append(
                f"    ,COUNT(DISTINCT CASE WHEN d.event_code='{ec}' AND {wc} "
                f"THEN d.event_date END) AS {feat_name(a, 'days', w)}"
            )
            cols.append(
                f"    ,CAST(SIGN(COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} "
                f"THEN d.daily_cnt ELSE 0 END), 0)) AS INT) AS {feat_name(a, 'ever', w)}"
            )
            cols.append(
                f"    ,MAX(CASE WHEN d.event_code='{ec}' AND {wc} "
                f"THEN d.daily_cnt END) AS {feat_name(a, 'max_daily', w)}"
            )
    return cols


def _gen_dim2_cols():
    """Dim 2: avg_daily / std_daily / cv_daily / min_daily × 7 windows × 65 events
    avg = SUM(cnt) / COUNT(DISTINCT date)  (活跃天均值)
    std = sqrt(E[X^2] - E[X]^2) 利用 daily_cnt_sq 预算列
    cv  = std / avg
    """
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in WINDOWS_WITH_ALL:
            wc = window_cond("d.days_back", w)
            cnt_expr = (f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} "
                        f"THEN d.daily_cnt ELSE 0 END), 0)")
            days_expr = (f"NULLIF(COUNT(DISTINCT CASE WHEN d.event_code='{ec}' AND {wc} "
                         f"THEN d.event_date END), 0)")
            sq_expr = (f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} "
                       f"THEN d.daily_cnt * d.daily_cnt ELSE 0 END), 0)")

            avg_name = feat_name(a, "avg_daily", w)
            std_name = feat_name(a, "std_daily", w)
            cv_name = feat_name(a, "cv_daily", w)
            min_name = feat_name(a, "min_daily", w)

            cols.append(f"    ,{cnt_expr} / {days_expr} AS {avg_name}")
            cols.append(
                f"    ,SQRT(GREATEST({sq_expr} / {days_expr} "
                f"- POW({cnt_expr} / {days_expr}, 2), 0)) AS {std_name}"
            )
            cols.append(
                f"    ,SQRT(GREATEST({sq_expr} / {days_expr} "
                f"- POW({cnt_expr} / {days_expr}, 2), 0)) "
                f"/ NULLIF({cnt_expr} / {days_expr}, 0) AS {cv_name}"
            )
            cols.append(
                f"    ,MIN(CASE WHEN d.event_code='{ec}' AND {wc} "
                f"THEN d.daily_cnt END) AS {min_name}"
            )
    return cols


def _gen_dim3_cols():
    """Dim 3: ratio pairs"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w_short, w_long in DIM_CONFIG[3]["pairs"]:
            wc_s = window_cond("d.days_back", w_short)
            wc_l = window_cond("d.days_back", w_long)
            cnt_s = (f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc_s} "
                     f"THEN d.daily_cnt ELSE 0 END), 0)")
            cnt_l = (f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc_l} "
                     f"THEN d.daily_cnt ELSE 0 END), 0)")
            s_label = f"{w_short}d" if w_short != ALL_WINDOW else "all"
            l_label = f"{w_long}d" if w_long != ALL_WINDOW else "all"
            name = f"{a}_ratio_{w_short}_{l_label}"
            cols.append(f"    ,{cnt_s} / NULLIF({cnt_l}, 0) AS {name}")
    return cols


def _gen_dim4_cols():
    """Dim 4: delta / chg_rate / accel for equal-length period pairs"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for p in DIM_CONFIG[4]["periods"]:
            wc_recent = window_cond("d.days_back", p)
            wc_double = window_cond("d.days_back", p * 2)
            cnt_recent = (f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc_recent} "
                          f"THEN d.daily_cnt ELSE 0 END), 0)")
            cnt_double = (f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc_double} "
                          f"THEN d.daily_cnt ELSE 0 END), 0)")
            cnt_prev = f"({cnt_double} - {cnt_recent})"

            cols.append(f"    ,({cnt_recent} - {cnt_prev}) AS {feat_name(a, 'delta', p)}")
            cols.append(
                f"    ,({cnt_recent} - {cnt_prev}) / NULLIF({cnt_prev} + 1, 0) "
                f"AS {feat_name(a, 'chg_rate', p)}"
            )
            cols.append(
                f"    ,CAST(SIGN({cnt_recent} - {cnt_prev}) AS INT) "
                f"AS {feat_name(a, 'accel', p)}"
            )
    return cols


def _gen_dim5_simple_cols():
    """Dim 5 simple: days_since_last / days_since_first"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        cols.append(
            f"    ,MIN(CASE WHEN d.event_code='{ec}' THEN d.days_back END) "
            f"AS {feat_name(a, 'days_since_last')}"
        )
        cols.append(
            f"    ,MAX(CASE WHEN d.event_code='{ec}' THEN d.days_back END) "
            f"AS {feat_name(a, 'days_since_first')}"
        )
    return cols


def sql_job_a(dt: str, mode: str) -> str:
    """Job A: Dim 1-4 + Dim5-simple，FROM daily_cnt"""
    anchor = f"'{dt}'" if mode == "t1" else "b.anchor_date"
    group_cols = "b.loan_account_id" if mode == "t1" else "b.loan_account_id, b.anchor_date"
    select_extra = "" if mode == "t1" else "\n    ,b.anchor_date"

    all_cols = _gen_dim1_cols() + _gen_dim2_cols() + _gen_dim3_cols() + _gen_dim4_cols() + _gen_dim5_simple_cols()

    daily_cnt_src = TABLE["daily_cnt"]
    base_src = TABLE["base"] if mode == "t1" else TABLE.get("hist_base", TABLE["base"])

    return f"""
DROP TABLE IF EXISTS {TABLE['feat_a']};
CREATE TABLE {TABLE['feat_a']} STORED AS PARQUET AS
SELECT
    b.loan_account_id{select_extra}
{chr(10).join(all_cols)}
FROM {base_src} b
LEFT JOIN (
    SELECT loan_account_id, event_code, event_date, daily_cnt,
           daily_cnt * daily_cnt AS daily_cnt_sq,
           DATEDIFF({anchor}, event_date) AS days_back
    FROM {daily_cnt_src}
    WHERE event_date >= DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS})
      AND event_date < {anchor}
) d ON b.loan_account_id = d.loan_account_id
GROUP BY {group_cols};
"""


# ═══════════════════════════════════════════════════════════════
# Job B: Dim 5 complex
# ═══════════════════════════════════════════════════════════════

def _gen_dim5_streak_gap_cols():
    """max_streak / max_gap 列，从 streak_len / day_seq CTE 聚合"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[5]["windowed"]["max_streak"]:
            wc = f"streak_min_db <= {w}"
            cols.append(
                f"    ,MAX(CASE WHEN sl.event_code='{ec}' AND {wc} "
                f"THEN sl.streak_length END) AS {feat_name(a, 'max_streak', w)}"
            )
        for w in DIM_CONFIG[5]["windowed"]["max_gap"]:
            wc = window_cond("ds.days_back", w)
            cols.append(
                f"    ,MAX(CASE WHEN ds.event_code='{ec}' AND {wc} AND ds.gap_days IS NOT NULL "
                f"THEN ds.gap_days END) AS {feat_name(a, 'max_gap', w)}"
            )
    return cols


def _gen_dim5_slope_cols():
    """slope 列：线性回归 (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x^2)"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[5]["windowed"]["slope"]:
            wc = window_cond("ds.days_back", w)
            n   = f"COUNT(CASE WHEN ds.event_code='{ec}' AND {wc} THEN 1 END)"
            sx  = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.days_back ELSE 0 END)"
            sy  = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.daily_cnt ELSE 0 END)"
            sxy = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.days_back * ds.daily_cnt ELSE 0 END)"
            sx2 = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.days_back * ds.days_back ELSE 0 END)"
            cols.append(
                f"    ,({n} * {sxy} - {sx} * {sy}) "
                f"/ NULLIF({n} * {sx2} - {sx} * {sx}, 0) "
                f"AS {feat_name(a, 'slope', w)}"
            )
    return cols


def _gen_dim5_ewm_cols():
    """ewm 列：衰减加权均值 SUM(cnt * 0.7^days_back) / SUM(0.7^days_back)"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[5]["windowed"]["ewm"]:
            wc = window_cond("ds.days_back", w)
            num = (f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} "
                   f"THEN ds.daily_cnt * POW(0.7, ds.days_back) ELSE 0 END)")
            den = (f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} "
                   f"THEN POW(0.7, ds.days_back) ELSE 0 END)")
            cols.append(f"    ,{num} / NULLIF({den}, 0) AS {feat_name(a, 'ewm', w)}")
    return cols


def _gen_dim5_active_gap_cols():
    """active_gap_avg / active_gap_std 列"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[5]["windowed"]["active_gap_avg"]:
            wc = window_cond("ds.days_back", w)
            gc = f"ds.gap_days IS NOT NULL AND ds.event_code='{ec}' AND {wc}"
            cols.append(f"    ,AVG(CASE WHEN {gc} THEN ds.gap_days END) AS {feat_name(a, 'active_gap_avg', w)}")
            cols.append(f"    ,STDDEV(CASE WHEN {gc} THEN ds.gap_days END) AS {feat_name(a, 'active_gap_std', w)}")
    return cols


def sql_job_b(dt: str, mode: str) -> str:
    """Job B: Dim 5 complex — streak/gap/slope/ewm/active_gap"""
    anchor = f"'{dt}'" if mode == "t1" else "b.anchor_date"
    base_src = TABLE["base"] if mode == "t1" else TABLE.get("hist_base", TABLE["base"])

    streak_cols = _gen_dim5_streak_gap_cols()
    slope_cols = _gen_dim5_slope_cols()
    ewm_cols = _gen_dim5_ewm_cols()
    gap_cols = _gen_dim5_active_gap_cols()

    all_cols = streak_cols + slope_cols + ewm_cols + gap_cols

    return f"""
DROP TABLE IF EXISTS {TABLE['feat_b']};
CREATE TABLE {TABLE['feat_b']} STORED AS PARQUET AS
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
    INNER JOIN {base_src} b ON d.loan_account_id = b.loan_account_id
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
        MIN(days_back) AS streak_min_db,
        COUNT(*) AS streak_length
    FROM streak_calc
    GROUP BY loan_account_id, event_code, streak_grp
)
SELECT
    COALESCE(sl.loan_account_id, ds.loan_account_id) AS loan_account_id
{chr(10).join(all_cols)}
FROM (SELECT DISTINCT loan_account_id FROM day_seq) uid
LEFT JOIN streak_len sl ON uid.loan_account_id = sl.loan_account_id
LEFT JOIN day_seq ds ON uid.loan_account_id = ds.loan_account_id
GROUP BY COALESCE(sl.loan_account_id, ds.loan_account_id);
"""


# ═══════════════════════════════════════════════════════════════
# Job C: Dim 6 — 时间间隔（通道 B: event_log）
# ═══════════════════════════════════════════════════════════════

def _gen_dim6_cols():
    """intv_min / intv_avg / intv_max / intv_std / intv_cv"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[6]["windows"]:
            wc = window_cond("itv.days_back", w)
            base_cond = f"itv.event_code='{ec}' AND {wc}"
            cols.append(f"    ,MIN(CASE WHEN {base_cond} THEN itv.gap_hours END) AS {feat_name(a, 'intv_min', w)}")
            cols.append(f"    ,AVG(CASE WHEN {base_cond} THEN itv.gap_hours END) AS {feat_name(a, 'intv_avg', w)}")
            cols.append(f"    ,MAX(CASE WHEN {base_cond} THEN itv.gap_hours END) AS {feat_name(a, 'intv_max', w)}")
            cols.append(f"    ,STDDEV(CASE WHEN {base_cond} THEN itv.gap_hours END) AS {feat_name(a, 'intv_std', w)}")
            cols.append(
                f"    ,STDDEV(CASE WHEN {base_cond} THEN itv.gap_hours END) "
                f"/ NULLIF(AVG(CASE WHEN {base_cond} THEN itv.gap_hours END), 0) "
                f"AS {feat_name(a, 'intv_cv', w)}"
            )
    return cols


def sql_job_c(dt: str, mode: str) -> str:
    """Job C: Dim 6 intervals — FROM event_log"""
    anchor = f"'{dt}'" if mode == "t1" else "b.anchor_date"
    base_src = TABLE["base"] if mode == "t1" else TABLE.get("hist_base", TABLE["base"])

    dim6_cols = _gen_dim6_cols()

    return f"""
DROP TABLE IF EXISTS {TABLE['feat_c']};
CREATE TABLE {TABLE['feat_c']} STORED AS PARQUET AS
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
    INNER JOIN {base_src} b
        ON e.loan_account_id = b.loan_account_id AND e.user_id = b.user_id
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
# Job D: Dim 7 — A→B 序列 + 跨事件比率
# ═══════════════════════════════════════════════════════════════

def _pair_alias(ev_a: str, ev_b: str) -> str:
    return f"{EVENT_CONFIG[ev_a]['alias']}_to_{EVENT_CONFIG[ev_b]['alias']}"


def sql_job_d(dt: str, mode: str) -> str:
    """Job D: Dim 7 sequence pairs — FROM event_log"""
    anchor = f"'{dt}'" if mode == "t1" else "b.anchor_date"
    base_src = TABLE["base"] if mode == "t1" else TABLE.get("hist_base", TABLE["base"])

    pair_ctes = []
    pair_select_parts = []
    pair_join_parts = []

    for idx, (ev_a, ev_b, win_h, label) in enumerate(PAIR_CONFIG):
        pname = f"p{idx}"
        pa = _pair_alias(ev_a, ev_b)
        win_sec = int(win_h * 3600)

        pair_ctes.append(f"""
{pname} AS (
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
    LEFT JOIN evt_filtered b
        ON a.loan_account_id = b.loan_account_id
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
        AS {pa}_time_min_all""")

        if idx == 0:
            pair_join_parts.append(f"FROM {pname}")
        else:
            pair_join_parts.append(
                f"FULL OUTER JOIN {pname} ON p0.loan_account_id = {pname}.loan_account_id"
            )

    ctes_sql = ",\n".join(pair_ctes)
    selects_sql = "".join(pair_select_parts)

    left_joins = "\n".join(
        f"LEFT JOIN {pname} ON uid.loan_account_id = {pname}.loan_account_id"
        for pname in [f"p{i}" for i in range(len(PAIR_CONFIG))]
    )

    rate_chg_cols = []
    for idx, (ev_a, ev_b, _, _) in enumerate(PAIR_CONFIG):
        pa = _pair_alias(ev_a, ev_b)
        rate_chg_cols.append(f"    ,NULL AS {pa}_rate_chg")

    rate_chg_sql = "\n".join(rate_chg_cols)

    return f"""
DROP TABLE IF EXISTS {TABLE['feat_d']};
CREATE TABLE {TABLE['feat_d']} STORED AS PARQUET AS
WITH evt_filtered AS (
    SELECT
        e.loan_account_id,
        e.event_code,
        e.created_date
    FROM {TABLE['event_log']} e
    INNER JOIN {base_src} b
        ON e.loan_account_id = b.loan_account_id AND e.user_id = b.user_id
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
{rate_chg_sql}
FROM uid
{left_joins}
GROUP BY uid.loan_account_id;
"""


# ═══════════════════════════════════════════════════════════════
# Merge: 合并 4 个 Job + 跨事件比率
# ═══════════════════════════════════════════════════════════════

def _collect_job_a_cols():
    """收集 Job A 全部列名（不含 loan_account_id）"""
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in WINDOWS_WITH_ALL:
            cols.append(feat_name(a, "cnt", w))
            cols.append(feat_name(a, "days", w))
            cols.append(feat_name(a, "ever", w))
            cols.append(feat_name(a, "max_daily", w))
        for w in WINDOWS_WITH_ALL:
            cols.append(feat_name(a, "avg_daily", w))
            cols.append(feat_name(a, "std_daily", w))
            cols.append(feat_name(a, "cv_daily", w))
            cols.append(feat_name(a, "min_daily", w))
        for w_s, w_l in DIM_CONFIG[3]["pairs"]:
            l_label = f"{w_l}d" if w_l != ALL_WINDOW else "all"
            cols.append(f"{a}_ratio_{w_s}_{l_label}")
        for p in DIM_CONFIG[4]["periods"]:
            cols.append(feat_name(a, "delta", p))
            cols.append(feat_name(a, "chg_rate", p))
            cols.append(feat_name(a, "accel", p))
        cols.append(feat_name(a, "days_since_last"))
        cols.append(feat_name(a, "days_since_first"))
    return cols


def _collect_job_b_cols():
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[5]["windowed"]["max_streak"]:
            cols.append(feat_name(a, "max_streak", w))
        for w in DIM_CONFIG[5]["windowed"]["max_gap"]:
            cols.append(feat_name(a, "max_gap", w))
        for w in DIM_CONFIG[5]["windowed"]["slope"]:
            cols.append(feat_name(a, "slope", w))
        for w in DIM_CONFIG[5]["windowed"]["ewm"]:
            cols.append(feat_name(a, "ewm", w))
        for w in DIM_CONFIG[5]["windowed"]["active_gap_avg"]:
            cols.append(feat_name(a, "active_gap_avg", w))
        for w in DIM_CONFIG[5]["windowed"]["active_gap_std"]:
            cols.append(feat_name(a, "active_gap_std", w))
    return cols


def _collect_job_c_cols():
    cols = []
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[6]["windows"]:
            for agg in DIM_CONFIG[6]["aggs"]:
                cols.append(feat_name(a, agg, w))
    return cols


def _collect_job_d_cols():
    cols = []
    for ev_a, ev_b, _, _ in PAIR_CONFIG:
        pa = _pair_alias(ev_a, ev_b)
        cols.append(f"{pa}_cnt_all")
        cols.append(f"{pa}_rate_all")
        cols.append(f"{pa}_time_avg_all")
        cols.append(f"{pa}_time_min_all")
        cols.append(f"{pa}_rate_chg")
    return cols


def sql_merge(dt: str, mode: str) -> str:
    """Stage 3: 合并 feat_a/b/c/d + 19 个跨事件比率，显式列出所有列避免重复"""
    dt_partition = dt.replace("-", "") if mode == "t1" else "hist"

    a_cols = [f"    ,a.{c}" for c in _collect_job_a_cols()]
    b_cols = [f"    ,b.{c}" for c in _collect_job_b_cols()]
    c_cols = [f"    ,c.{c}" for c in _collect_job_c_cols()]
    d_cols = [f"    ,d.{c}" for c in _collect_job_d_cols()]

    cross_cols = []
    for name, numerator, denominator in CROSS_RATIO_CONFIG:
        cross_cols.append(f"    ,a.{numerator} / {denominator} AS {name}")

    all_select = (
        a_cols + b_cols + c_cols + d_cols + cross_cols
    )

    return f"""
DROP TABLE IF EXISTS {TABLE['features']}_tmp;
CREATE TABLE {TABLE['features']}_tmp STORED AS PARQUET AS
SELECT
    a.loan_account_id
{chr(10).join(all_select)}
FROM {TABLE['feat_a']} a
LEFT JOIN {TABLE['feat_b']} b ON a.loan_account_id = b.loan_account_id
LEFT JOIN {TABLE['feat_c']} c ON a.loan_account_id = c.loan_account_id
LEFT JOIN {TABLE['feat_d']} d ON a.loan_account_id = d.loan_account_id;

-- 写入分区表
INSERT OVERWRITE TABLE {TABLE['features']}
    PARTITION(dt = '{dt_partition}')
SELECT * FROM {TABLE['features']}_tmp;

DROP TABLE IF EXISTS {TABLE['features']}_tmp;
"""


# ═══════════════════════════════════════════════════════════════
# DDL
# ═══════════════════════════════════════════════════════════════

def sql_create_tables() -> str:
    """生成所有建表 DDL"""
    return f"""
-- ====== 人群 base 表 ======
DROP TABLE IF EXISTS {TABLE['base']};
CREATE TABLE IF NOT EXISTS {TABLE['base']} (
    loan_account_id STRING,
    user_id         STRING,
    batch_date      STRING
) STORED AS PARQUET;

-- ====== daily_cnt 中间层 ======
CREATE TABLE IF NOT EXISTS {TABLE['daily_cnt']} (
    loan_account_id STRING,
    event_code      STRING,
    daily_cnt       INT,
    daily_dur_sum   DOUBLE,
    daily_dur_max   DOUBLE
) PARTITIONED BY (event_date STRING)
STORED AS PARQUET;

-- ====== Job 临时表 ======
-- feat_a / feat_b / feat_c / feat_d 由各 Job SQL 的 CREATE TABLE ... AS 自动创建

-- ====== 最终特征表 ======
-- 列数过多（~8104），采用 CREATE TABLE ... AS 由 merge 阶段自动创建
-- 首次运行时需先执行各 Job 再 merge
CREATE TABLE IF NOT EXISTS {TABLE['features']} (
    loan_account_id STRING
) PARTITIONED BY (dt STRING)
STORED AS PARQUET;
"""


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

JOB_GENERATORS = {
    "ddl":       lambda dt, mode: sql_create_tables(),
    "base":      lambda dt, mode: sql_base_table(dt),
    "daily_cnt": lambda dt, mode: sql_daily_cnt_sliding(dt),
    "A":         sql_job_a,
    "B":         sql_job_b,
    "C":         sql_job_c,
    "D":         sql_job_d,
    "merge":     sql_merge,
}

ALL_JOBS = ["ddl", "base", "daily_cnt", "A", "B", "C", "D", "merge"]


def generate_sql(mode: str, job: str, dt: str) -> str:
    """生成指定 Job 的 SQL"""
    gen = JOB_GENERATORS.get(job)
    if gen is None:
        raise ValueError(f"Unknown job: {job}. Available: {list(JOB_GENERATORS.keys())}")
    return gen(dt, mode)


def count_features():
    """统计各维度特征数"""
    n_events = len(EVENT_CONFIG)
    n_win = len(WINDOWS_WITH_ALL)
    counts = {
        "Dim1 cnt":       n_events * n_win,
        "Dim1 days":      n_events * n_win,
        "Dim1 ever":      n_events * n_win,
        "Dim1 max_daily": n_events * n_win,
        "Dim2 avg_daily": n_events * n_win,
        "Dim2 std_daily": n_events * n_win,
        "Dim2 cv_daily":  n_events * n_win,
        "Dim2 min_daily": n_events * n_win,
        "Dim3 ratio":     n_events * len(DIM_CONFIG[3]["pairs"]),
        "Dim4 delta":     n_events * len(DIM_CONFIG[4]["periods"]),
        "Dim4 chg_rate":  n_events * len(DIM_CONFIG[4]["periods"]),
        "Dim4 accel":     n_events * len(DIM_CONFIG[4]["periods"]),
        "Dim5 simple":    n_events * 2,
    }
    dim5_complex = 0
    for feat_type, windows in DIM_CONFIG[5]["windowed"].items():
        dim5_complex += n_events * len(windows)
    counts["Dim5 complex"] = dim5_complex
    counts["Dim6 interval"] = n_events * len(DIM_CONFIG[6]["aggs"]) * len(DIM_CONFIG[6]["windows"])
    counts["Dim7 pairs"] = len(PAIR_CONFIG) * len(DIM_CONFIG[7]["per_pair_aggs"])
    counts["Cross ratio"] = len(CROSS_RATIO_CONFIG)

    total = sum(counts.values())
    print(f"\n{'='*50}")
    print(f"特征总量统计（{n_events} 事件）")
    print(f"{'='*50}")
    for k, v in counts.items():
        print(f"  {k:25s} : {v:>6,d}")
    print(f"  {'─'*35}")
    print(f"  {'TOTAL':25s} : {total:>6,d}")
    return total


def main():
    parser = argparse.ArgumentParser(description="埋点 T+1 特征 SQL 生成器")
    parser.add_argument("--mode", choices=["t1", "hist"], default="t1")
    parser.add_argument("--job", default="all", help="Job 名称，逗号分隔或 all")
    parser.add_argument("--dt", default="2026-04-08", help="锚点日期 YYYY-MM-DD")
    parser.add_argument("--output", default="sql", help="SQL 输出目录")
    parser.add_argument("--count", action="store_true", help="仅统计特征数量")
    args = parser.parse_args()

    if args.count:
        count_features()
        return

    jobs = ALL_JOBS if args.job == "all" else [j.strip() for j in args.job.split(",")]

    os.makedirs(args.output, exist_ok=True)

    for job in jobs:
        sql = generate_sql(args.mode, job, args.dt)
        out_path = os.path.join(args.output, f"{job}.sql")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(sql)
        n_lines = sql.count("\n")
        print(f"[OK] {job:12s} -> {out_path} ({n_lines:,d} lines)")


if __name__ == "__main__":
    main()
