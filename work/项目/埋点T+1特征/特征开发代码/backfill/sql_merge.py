"""
merge 离线回溯 SQL 生成器

从 4 张已落地的 feat 表（{output_prefix}_feat_a/b/c/d）合并，
CTAS 写入最终特征表 {output_prefix}_features。
"""

from config import (
    EVENT_CONFIG, PAIR_ALIASES, CROSS_RATIO_CONFIG,
    WINDOWS_WITH_ALL, RATIO_PAIRS, DELTA_PERIODS,
    STREAK_WINDOWS, GAP_WINDOWS, SLOPE_WINDOWS, EWM_WINDOWS, ACTIVE_GAP_WINDOWS,
    INTV_WINDOWS,
)

def _wl(w):
    return "all" if w == "all" else f"{w}d"

def _collect_a():
    cols = []
    for a in EVENT_CONFIG.values():
        for w in WINDOWS_WITH_ALL:
            wl = _wl(w)
            cols += [f"a.{a}_cnt_{wl}", f"a.{a}_days_{wl}", f"a.{a}_ever_{wl}", f"a.{a}_max_daily_{wl}"]
        for w in WINDOWS_WITH_ALL:
            wl = _wl(w)
            cols += [f"a.{a}_avg_daily_{wl}", f"a.{a}_std_daily_{wl}", f"a.{a}_cv_daily_{wl}", f"a.{a}_min_daily_{wl}"]
        for ws, wl_v in RATIO_PAIRS:
            cols.append(f"a.{a}_ratio_{ws}_{_wl(wl_v)}")
        for p in DELTA_PERIODS:
            cols += [f"a.{a}_delta_{p}d", f"a.{a}_chg_rate_{p}d", f"a.{a}_accel_{p}d"]
        cols += [f"a.{a}_days_since_last", f"a.{a}_days_since_first"]
    return cols

def _collect_b():
    cols = []
    for a in EVENT_CONFIG.values():
        for w in STREAK_WINDOWS:
            cols.append(f"b.{a}_max_streak_{w}d")
        for w in GAP_WINDOWS:
            cols.append(f"b.{a}_max_gap_{w}d")
        for w in SLOPE_WINDOWS:
            cols.append(f"b.{a}_slope_{w}d")
        for w in EWM_WINDOWS:
            cols.append(f"b.{a}_ewm_{w}d")
        for w in ACTIVE_GAP_WINDOWS:
            cols += [f"b.{a}_active_gap_avg_{w}d", f"b.{a}_active_gap_std_{w}d"]
    return cols

def _collect_c():
    cols = []
    for a in EVENT_CONFIG.values():
        for w in INTV_WINDOWS:
            wl = _wl(w)
            cols += [f"c.{a}_intv_min_{wl}", f"c.{a}_intv_avg_{wl}", f"c.{a}_intv_max_{wl}",
                     f"c.{a}_intv_std_{wl}", f"c.{a}_intv_cv_{wl}"]
    return cols

def _collect_d():
    cols = []
    for aa, ab in PAIR_ALIASES:
        pa = f"{aa}_to_{ab}"
        cols += [f"d.{pa}_cnt_all", f"d.{pa}_rate_all",
                 f"d.{pa}_time_avg_all", f"d.{pa}_time_min_all", f"d.{pa}_rate_chg"]
    return cols

def _cross_ratio_cols():
    return [f"a.{num}/{den} AS {name}" for name, num, den in CROSS_RATIO_CONFIG]

def sql_merge(output_prefix: str) -> str:
    """
    从 {output_prefix}_feat_a/b/c/d 合并，写入 {output_prefix}_features。
    """
    fa = f"{output_prefix}_feat_a"
    fb = f"{output_prefix}_feat_b"
    fc = f"{output_prefix}_feat_c"
    fd = f"{output_prefix}_feat_d"
    table_write = f"{output_prefix}_features"

    all_cols = (
        [f"    ,{c}" for c in _collect_a()]
        + [f"    ,{c}" for c in _collect_b()]
        + [f"    ,{c}" for c in _collect_c()]
        + [f"    ,{c}" for c in _collect_d()]
        + [f"    ,{c}" for c in _cross_ratio_cols()]
    )
    return f"""
CREATE TABLE {table_write} AS
SELECT
    a.loan_account_id
{chr(10).join(all_cols)}
    ,a.trace_id
    ,a.anchor_date
FROM {fa} a
LEFT JOIN {fb} b ON a.trace_id = b.trace_id AND a.loan_account_id = b.loan_account_id
LEFT JOIN {fc} c ON a.trace_id = c.trace_id AND a.loan_account_id = c.loan_account_id
LEFT JOIN {fd} d ON a.trace_id = d.trace_id AND a.loan_account_id = d.loan_account_id
"""
