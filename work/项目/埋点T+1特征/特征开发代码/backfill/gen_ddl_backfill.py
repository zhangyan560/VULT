"""
生成离线回溯 5 张输出表的 CREATE TABLE DDL，本地运行后输出到 ddl/ 目录。

用法：
    python gen_ddl_backfill.py --output-db ec_risk_model_dev --output-dir ddl/
"""

import argparse
import os

from config import (
    EVENT_CONFIG, WINDOWS_WITH_ALL, RATIO_PAIRS, DELTA_PERIODS,
    STREAK_WINDOWS, GAP_WINDOWS, SLOPE_WINDOWS, EWM_WINDOWS, ACTIVE_GAP_WINDOWS,
    INTV_WINDOWS, PAIR_ALIASES, CROSS_RATIO_CONFIG,
)

ALL_WINDOW = "all"

def _wl(w):
    return "all" if w == ALL_WINDOW else f"{w}d"


# ══════════════════ 各表列定义 ═════════════════════════════════════════════

def _feat_a_cols():
    cols = []
    for a in EVENT_CONFIG.values():
        for w in WINDOWS_WITH_ALL:
            wl = _wl(w)
            cols += [
                f"    {a}_cnt_{wl}        BIGINT",
                f"    ,{a}_days_{wl}       BIGINT",
                f"    ,{a}_ever_{wl}       INT",
                f"    ,{a}_max_daily_{wl}  BIGINT",
                f"    ,{a}_avg_daily_{wl}  DOUBLE",
                f"    ,{a}_std_daily_{wl}  DOUBLE",
                f"    ,{a}_cv_daily_{wl}   DOUBLE",
                f"    ,{a}_min_daily_{wl}  BIGINT",
            ]
        for ws, wlv in RATIO_PAIRS:
            cols.append(f"    ,{a}_ratio_{ws}_{_wl(wlv)} DOUBLE")
        for p in DELTA_PERIODS:
            cols += [
                f"    ,{a}_delta_{p}d    BIGINT",
                f"    ,{a}_chg_rate_{p}d DOUBLE",
                f"    ,{a}_accel_{p}d    INT",
            ]
        cols += [
            f"    ,{a}_days_since_last  BIGINT",
            f"    ,{a}_days_since_first BIGINT",
        ]
    return cols

def _feat_b_cols():
    cols = []
    for a in EVENT_CONFIG.values():
        for w in STREAK_WINDOWS:
            cols.append(f"    ,{a}_max_streak_{w}d BIGINT")
        for w in GAP_WINDOWS:
            cols.append(f"    ,{a}_max_gap_{w}d    BIGINT")
        for w in SLOPE_WINDOWS:
            cols.append(f"    ,{a}_slope_{w}d      DOUBLE")
        for w in EWM_WINDOWS:
            cols.append(f"    ,{a}_ewm_{w}d        DOUBLE")
        for w in ACTIVE_GAP_WINDOWS:
            cols += [
                f"    ,{a}_active_gap_avg_{w}d DOUBLE",
                f"    ,{a}_active_gap_std_{w}d DOUBLE",
            ]
    return cols

def _feat_c_cols():
    cols = []
    for a in EVENT_CONFIG.values():
        for w in INTV_WINDOWS:
            wl = _wl(w)
            cols += [
                f"    ,{a}_intv_min_{wl} DOUBLE",
                f"    ,{a}_intv_avg_{wl} DOUBLE",
                f"    ,{a}_intv_max_{wl} DOUBLE",
                f"    ,{a}_intv_std_{wl} DOUBLE",
                f"    ,{a}_intv_cv_{wl}  DOUBLE",
            ]
    return cols

def _feat_d_cols():
    cols = []
    for aa, ab in PAIR_ALIASES:
        pa = f"{aa}_to_{ab}"
        cols += [
            f"    ,{pa}_cnt_all      BIGINT",
            f"    ,{pa}_rate_all     DOUBLE",
            f"    ,{pa}_time_avg_all DOUBLE",
            f"    ,{pa}_time_min_all DOUBLE",
            f"    ,{pa}_rate_chg     DOUBLE",
        ]
    return cols

def _features_cols():
    cols = _feat_a_cols() + _feat_b_cols() + _feat_c_cols() + _feat_d_cols()
    for name, _, _ in CROSS_RATIO_CONFIG:
        cols.append(f"    ,{name} DOUBLE")
    return cols


# ══════════════════ DDL 生成 ═══════════════════════════════════════════════

HEADER = """-- 离线回溯输出表 DDL
-- 生成方式：python gen_ddl_backfill.py
-- 注意：DataPilot 表管理建表时不要填写 STORED AS，平台自动处理

"""

def _build_ddl(db, table_suffix, comment, cols, partition=True):
    full = f"{db}.yz_event3_t1_backfill_{table_suffix}"
    # 确保第一个特征列不带前置逗号（base 列末尾已有逗号）
    if cols and cols[0].lstrip().startswith(","):
        cols = ["    " + cols[0].lstrip().lstrip(",")] + cols[1:]
    col_str = "\n".join(cols)
    partition_clause = (
        "PARTITIONED BY (anchor_ym STRING COMMENT '锚点年月 yyyy-MM，用于分区管理')"
        if partition else ""
    )
    return f"""CREATE TABLE {full} (
    trace_id        STRING  COMMENT 'trace 唯一标识',
    loan_account_id STRING  COMMENT '贷款账户 ID',
    anchor_date     STRING  COMMENT '特征计算锚点日期 yyyy-MM-dd',
{col_str}
) COMMENT '{comment}'
{partition_clause};
"""


def generate_all(output_db, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    tables = [
        ("feat_a",    "埋点T+1回溯 feat_a（Dim1-4+Dim5-simple）", _feat_a_cols()),
        ("feat_b",    "埋点T+1回溯 feat_b（Dim5-complex）",        _feat_b_cols()),
        ("feat_c",    "埋点T+1回溯 feat_c（Dim6 时间间隔）",       _feat_c_cols()),
        ("feat_d",    "埋点T+1回溯 feat_d（Dim7 A→B序列）",        _feat_d_cols()),
        ("features",  "埋点T+1回溯 宽表（全量合并）",              _features_cols()),
    ]

    all_ddl_lines = [HEADER]

    for suffix, comment, cols in tables:
        ddl = _build_ddl(output_db, suffix, comment, cols)
        fname = os.path.join(output_dir, f"ddl_backfill_{suffix}.sql")
        with open(fname, "w") as f:
            f.write(ddl)
        all_ddl_lines.append(f"-- ===== {suffix} =====\n" + ddl)
        print(f"  生成 {fname}  ({len(cols)} 列)")

    all_path = os.path.join(output_dir, "ddl_backfill_all.sql")
    with open(all_path, "w") as f:
        f.write("\n".join(all_ddl_lines))
    print(f"\n  合并文件 → {all_path}")


def main():
    parser = argparse.ArgumentParser(description="生成离线回溯 DDL")
    parser.add_argument("--output-db",  default="ec_risk_model_dev", help="目标数据库")
    parser.add_argument("--output-dir", default="ddl", help="输出目录")
    args = parser.parse_args()
    print(f"[gen_ddl_backfill] 目标库：{args.output_db}")
    generate_all(args.output_db, args.output_dir)
    print("[gen_ddl_backfill] 完成")


if __name__ == "__main__":
    main()
