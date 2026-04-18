"""
feat_b 离线回溯 SQL 生成器（Dim5-complex: streak/gap/slope/ewm/active_gap）

两步法：
  Step1 全局计算 gap_days（LAG 与 anchor 无关），覆盖全部相关用户
  Step2 JOIN trace，per-trace 过滤窗口，计算 days_back
  Step3 streak 按 (trace_id, loan_account_id, event_code) 分区计算
"""

from config import (
    EVENT_CONFIG,
    STREAK_WINDOWS, GAP_WINDOWS, SLOPE_WINDOWS, EWM_WINDOWS, ACTIVE_GAP_WINDOWS,
    MAX_LOOKBACK_DAYS,
)

def _wc_days(col, w):
    return f"{col} BETWEEN 1 AND {w}"

def _fn(alias, agg, w=None):
    if w is None:
        return f"{alias}_{agg}"
    return f"{alias}_{agg}_{w}d"

def _streak_gap_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in STREAK_WINDOWS:
            cols.append(f"    ,MAX(CASE WHEN sl.event_code='{ec}' AND sl.streak_min_db <= {w} THEN sl.streak_length END) AS {_fn(a,'max_streak',w)}")
        for w in GAP_WINDOWS:
            cols.append(f"    ,MAX(CASE WHEN ds.event_code='{ec}' AND {_wc_days('ds.days_back',w)} AND ds.gap_days IS NOT NULL THEN ds.gap_days END) AS {_fn(a,'max_gap',w)}")
    return cols

def _slope_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in SLOPE_WINDOWS:
            wc  = _wc_days("ds.days_back", w)
            n   = f"COUNT(CASE WHEN ds.event_code='{ec}' AND {wc} THEN 1 END)"
            sx  = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.days_back ELSE 0 END)"
            sy  = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.daily_cnt ELSE 0 END)"
            sxy = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.days_back*ds.daily_cnt ELSE 0 END)"
            sx2 = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.days_back*ds.days_back ELSE 0 END)"
            cols.append(f"    ,({n}*{sxy}-{sx}*{sy})/NULLIF({n}*{sx2}-{sx}*{sx},0) AS {_fn(a,'slope',w)}")
    return cols

def _ewm_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in EWM_WINDOWS:
            wc  = _wc_days("ds.days_back", w)
            num = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN ds.daily_cnt*POW(0.7,ds.days_back) ELSE 0 END)"
            den = f"SUM(CASE WHEN ds.event_code='{ec}' AND {wc} THEN POW(0.7,ds.days_back) ELSE 0 END)"
            cols.append(f"    ,{num}/NULLIF({den},0) AS {_fn(a,'ewm',w)}")
    return cols

def _active_gap_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in ACTIVE_GAP_WINDOWS:
            gc = f"ds.gap_days IS NOT NULL AND ds.event_code='{ec}' AND {_wc_days('ds.days_back',w)}"
            cols.append(f"    ,AVG(CASE WHEN {gc} THEN ds.gap_days END) AS {_fn(a,'active_gap_avg',w)}")
            cols.append(f"    ,STDDEV(CASE WHEN {gc} THEN ds.gap_days END) AS {_fn(a,'active_gap_std',w)}")
    return cols

def sql_feat_b(trace_table: str, output_prefix: str, min_anchor: str, max_anchor: str) -> str:
    table_write  = f"{output_prefix}_feat_b"
    daily_table  = f"{output_prefix}_daily_cnt"   # Step0 产出
    all_cols = _streak_gap_cols() + _slope_cols() + _ewm_cols() + _active_gap_cols()
    return f"""
CREATE TABLE {table_write} AS
WITH trace AS (
    SELECT trace_id, loan_account_id, TO_DATE(anchor_date) AS anchor_date
    FROM {trace_table}
),
-- Step1: 全局 gap_days（LAG 不依赖 anchor），直接读 Step0 产出的 daily_cnt
day_seq_raw AS (
    SELECT
        d.loan_account_id,
        d.event_code,
        d.event_date,
        d.daily_cnt,
        DATEDIFF(d.event_date,
            LAG(d.event_date) OVER (
                PARTITION BY d.loan_account_id, d.event_code ORDER BY d.event_date
            )) AS gap_days
    FROM {daily_table} d
    WHERE d.daily_cnt > 0
),
-- Step2: per-trace 展开，加 days_back
day_seq AS (
    SELECT
        t.trace_id,
        t.anchor_date,
        r.loan_account_id,
        r.event_code,
        r.event_date,
        r.daily_cnt,
        r.gap_days,
        DATEDIFF(t.anchor_date, r.event_date) AS days_back
    FROM trace t
    JOIN day_seq_raw r
        ON  t.loan_account_id = r.loan_account_id
        AND r.event_date >= DATE_SUB(t.anchor_date, {MAX_LOOKBACK_DAYS})
        AND r.event_date <  t.anchor_date
),
-- Step3: streak 分组，按 (trace_id, loan_account_id, event_code) 独立计算
streak_calc AS (
    SELECT
        trace_id, anchor_date, loan_account_id, event_code, event_date, days_back,
        DATEDIFF(event_date, '1970-01-01') - ROW_NUMBER() OVER (
            PARTITION BY trace_id, loan_account_id, event_code ORDER BY event_date
        ) AS streak_grp
    FROM day_seq
),
streak_len AS (
    SELECT
        trace_id, anchor_date, loan_account_id, event_code, streak_grp,
        MIN(days_back) AS streak_min_db,
        COUNT(*)       AS streak_length
    FROM streak_calc
    GROUP BY trace_id, anchor_date, loan_account_id, event_code, streak_grp
)
SELECT
    uid.loan_account_id
{chr(10).join(all_cols)}
    ,uid.trace_id
    ,uid.anchor_date
FROM (SELECT DISTINCT trace_id, anchor_date, loan_account_id FROM day_seq) uid
LEFT JOIN streak_len sl ON uid.trace_id = sl.trace_id AND uid.loan_account_id = sl.loan_account_id
LEFT JOIN day_seq    ds ON uid.trace_id = ds.trace_id AND uid.loan_account_id = ds.loan_account_id
GROUP BY uid.trace_id, uid.loan_account_id, uid.anchor_date
"""
