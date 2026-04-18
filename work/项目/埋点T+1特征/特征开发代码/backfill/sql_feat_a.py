"""
feat_a 离线回溯 SQL 生成器（Dim1-4 + Dim5-simple）

生成 CREATE TABLE ... AS SELECT，直接从 trace 表出发，JOIN daily_cnt 计算特征。
anchor_date 取 trace_created_date 的日期部分（TO_DATE），确保 T+1 语义（当天 0 点截止）。
"""

from config import (
    EVENT_CONFIG, WINDOWS_WITH_ALL, RATIO_PAIRS, DELTA_PERIODS,
    MAX_LOOKBACK_DAYS,
)

ALL_WINDOW = "all"

# ── 工具函数 ───────────────────────────────────────────────────────────────

def _wc(w):
    return "d.days_back >= 1" if w == ALL_WINDOW else f"d.days_back BETWEEN 1 AND {w}"

def _wl(w):
    return "all" if w == ALL_WINDOW else f"{w}d"

def _fn(alias, agg, w=None):
    if w is None:
        return f"{alias}_{agg}"
    return f"{alias}_{agg}_{_wl(w)}"

# ── 列生成（与 task03 完全一致）───────────────────────────────────────────

def _dim1_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in WINDOWS_WITH_ALL:
            wc = _wc(w)
            cols.append(f"    ,COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt ELSE 0 END),0) AS {_fn(a,'cnt',w)}")
            cols.append(f"    ,COUNT(DISTINCT CASE WHEN d.event_code='{ec}' AND {wc} THEN d.event_date END) AS {_fn(a,'days',w)}")
            cols.append(f"    ,CAST(SIGN(COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt ELSE 0 END),0)) AS INT) AS {_fn(a,'ever',w)}")
            cols.append(f"    ,MAX(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt END) AS {_fn(a,'max_daily',w)}")
    return cols

def _dim2_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in WINDOWS_WITH_ALL:
            wc   = _wc(w)
            cnt  = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt ELSE 0 END),0)"
            days = f"NULLIF(COUNT(DISTINCT CASE WHEN d.event_code='{ec}' AND {wc} THEN d.event_date END),0)"
            sq   = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt*d.daily_cnt ELSE 0 END),0)"
            cols.append(f"    ,{cnt}/{days} AS {_fn(a,'avg_daily',w)}")
            cols.append(f"    ,SQRT(GREATEST({sq}/{days}-POW({cnt}/{days},2),0)) AS {_fn(a,'std_daily',w)}")
            cols.append(f"    ,SQRT(GREATEST({sq}/{days}-POW({cnt}/{days},2),0))/NULLIF({cnt}/{days},0) AS {_fn(a,'cv_daily',w)}")
            cols.append(f"    ,MIN(CASE WHEN d.event_code='{ec}' AND {wc} THEN d.daily_cnt END) AS {_fn(a,'min_daily',w)}")
    return cols

def _dim3_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for ws, wl in RATIO_PAIRS:
            cnt_s = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(ws)} THEN d.daily_cnt ELSE 0 END),0)"
            cnt_l = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(wl)} THEN d.daily_cnt ELSE 0 END),0)"
            cols.append(f"    ,{cnt_s}/NULLIF({cnt_l},0) AS {a}_ratio_{ws}_{_wl(wl)}")
    return cols

def _dim4_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for p in DELTA_PERIODS:
            cr   = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(p)} THEN d.daily_cnt ELSE 0 END),0)"
            cd   = f"COALESCE(SUM(CASE WHEN d.event_code='{ec}' AND {_wc(p*2)} THEN d.daily_cnt ELSE 0 END),0)"
            prev = f"({cd}-{cr})"
            cols.append(f"    ,({cr}-{prev}) AS {_fn(a,'delta',p)}")
            cols.append(f"    ,({cr}-{prev})/NULLIF({prev}+1,0) AS {_fn(a,'chg_rate',p)}")
            cols.append(f"    ,CAST(SIGN({cr}-{prev}) AS INT) AS {_fn(a,'accel',p)}")
    return cols

def _dim5_simple_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        cols.append(f"    ,MIN(CASE WHEN d.event_code='{ec}' THEN d.days_back END) AS {_fn(a,'days_since_last')}")
        cols.append(f"    ,MAX(CASE WHEN d.event_code='{ec}' THEN d.days_back END) AS {_fn(a,'days_since_first')}")
    return cols

# ── SQL 生成 ───────────────────────────────────────────────────────────────

def sql_feat_a(trace_table: str, output_prefix: str, min_anchor: str, max_anchor: str) -> str:
    """
    trace_table   : 全限定表名，如 risk_data.yz_event3_firstloan_reloan_firstbase_lite
    output_prefix : 输出表名前缀，如 risk_data.yz_event3_backfill
                    → 读取 {output_prefix}_daily_cnt（Step0 产出）
                    → 写入 {output_prefix}_feat_a
    min_anchor    : yyyy-MM-dd，与 Step0 保持一致
    max_anchor    : yyyy-MM-dd（不含）
    """
    table_write  = f"{output_prefix}_feat_a"
    daily_table  = f"{output_prefix}_daily_cnt"   # Step0 产出
    all_cols = _dim1_cols() + _dim2_cols() + _dim3_cols() + _dim4_cols() + _dim5_simple_cols()
    return f"""
CREATE TABLE {table_write} AS
WITH trace AS (
    SELECT trace_id, loan_account_id, TO_DATE(anchor_date) AS anchor_date
    FROM {trace_table}
),
-- 读 Step0 计算好的 daily_cnt（已限定回溯人群 + 全局日期范围）
daily_pre AS (
    SELECT loan_account_id, event_code, event_date, daily_cnt
    FROM {daily_table}
),
-- per-trace 展开，计算 days_back
dj AS (
    SELECT
        t.trace_id,
        t.loan_account_id,
        t.anchor_date,
        d.event_code,
        d.event_date,
        d.daily_cnt,
        DATEDIFF(t.anchor_date, d.event_date) AS days_back
    FROM trace t
    LEFT JOIN daily_pre d
        ON  t.loan_account_id = d.loan_account_id
        AND d.event_date >= DATE_SUB(t.anchor_date, {MAX_LOOKBACK_DAYS})
        AND d.event_date <  t.anchor_date
)
SELECT
    d.loan_account_id
{chr(10).join(all_cols)}
    ,d.trace_id
    ,d.anchor_date
FROM dj d
GROUP BY d.trace_id, d.loan_account_id, d.anchor_date
"""
