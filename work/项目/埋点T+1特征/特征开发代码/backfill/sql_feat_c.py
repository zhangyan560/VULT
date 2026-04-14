"""
feat_c 离线回溯 SQL 生成器（Dim6 时间间隔）

两步法：
  Step1 全局计算 LAG(created_date)（与 anchor 无关），覆盖所有相关用户
  Step2 JOIN trace，per-trace 过滤窗口，计算 gap_hours / days_back
注意：trace 表无 user_id，event_log 仅按 loan_account_id 关联。
"""

from config import EVENT_CONFIG, INTV_WINDOWS, TABLE_EVENT_LOG, MAX_LOOKBACK_DAYS

def _wc(w):
    return "itv.days_back >= 1" if w == "all" else f"itv.days_back BETWEEN 1 AND {w}"

def _wl(w):
    return "all" if w == "all" else f"{w}d"

def _event_in_clause():
    return "(" + ",".join(f"'{e}'" for e in EVENT_CONFIG) + ")"

def _dim6_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in INTV_WINDOWS:
            wc = _wc(w)
            bc = f"itv.event_code='{ec}' AND {wc}"
            wl = _wl(w)
            cols.append(f"    ,MIN(CASE WHEN {bc} THEN itv.gap_hours END) AS {a}_intv_min_{wl}")
            cols.append(f"    ,AVG(CASE WHEN {bc} THEN itv.gap_hours END) AS {a}_intv_avg_{wl}")
            cols.append(f"    ,MAX(CASE WHEN {bc} THEN itv.gap_hours END) AS {a}_intv_max_{wl}")
            cols.append(f"    ,STDDEV(CASE WHEN {bc} THEN itv.gap_hours END) AS {a}_intv_std_{wl}")
            cols.append(f"    ,STDDEV(CASE WHEN {bc} THEN itv.gap_hours END)/NULLIF(AVG(CASE WHEN {bc} THEN itv.gap_hours END),0) AS {a}_intv_cv_{wl}")
    return cols

def sql_feat_c(trace_table: str, output_prefix: str, min_anchor: str, max_anchor: str) -> str:
    table_write = f"{output_prefix}_feat_c"
    # dt 分区过滤：yyyyMMdd 格式，多留 1 天缓冲
    return f"""
CREATE TABLE {table_write} AS
WITH trace AS (
    SELECT trace_id, loan_account_id, TO_DATE(anchor_date) AS anchor_date
    FROM {trace_table}
),
-- Step1: 全局 LAG，覆盖 [min_anchor-225, max_anchor) 的所有相关用户事件
raw_evt AS (
    SELECT
        e.loan_account_id,
        e.event_code,
        e.created_date,
        LAG(e.created_date) OVER (
            PARTITION BY e.loan_account_id, e.event_code ORDER BY e.created_date
        ) AS prev_created_date
    FROM {TABLE_EVENT_LOG} e
    INNER JOIN (SELECT DISTINCT loan_account_id FROM trace) ids
        ON e.loan_account_id = ids.loan_account_id
    WHERE e.dt >= REGEXP_REPLACE(CAST(DATE_SUB('{min_anchor}', {MAX_LOOKBACK_DAYS + 1}) AS STRING), '-', '')
      AND e.event_code IN {_event_in_clause()}
      AND e.loan_account_id IS NOT NULL
),
-- Step2: per-trace 展开，过滤各自窗口，计算 gap_hours / days_back
itv AS (
    SELECT
        t.trace_id,
        t.anchor_date,
        r.loan_account_id,
        r.event_code,
        DATEDIFF(t.anchor_date, TO_DATE(r.created_date)) AS days_back,
        (UNIX_TIMESTAMP(r.created_date) - UNIX_TIMESTAMP(r.prev_created_date)) / 3600.0 AS gap_hours
    FROM trace t
    JOIN raw_evt r
        ON  t.loan_account_id = r.loan_account_id
        AND TO_DATE(r.created_date) <  t.anchor_date
        AND TO_DATE(r.created_date) >= DATE_SUB(t.anchor_date, {MAX_LOOKBACK_DAYS})
        AND r.prev_created_date IS NOT NULL
)
SELECT
    itv.loan_account_id
{chr(10).join(_dim6_cols())}
    ,itv.trace_id
    ,itv.anchor_date
FROM itv
GROUP BY itv.trace_id, itv.loan_account_id, itv.anchor_date
"""
