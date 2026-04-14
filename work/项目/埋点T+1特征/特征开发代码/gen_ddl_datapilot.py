"""
埋点 T+1 — DataPilot 宽表 DDL 生成器

用途：本地运行，生成 feat_a / feat_b / feat_c / feat_d / features 的 CREATE TABLE DDL。
将输出粘贴到 DataPilot【数据开发 → 表管理】完成建表，建表库选 ec_risk_model_dev。

用法：
    python3 gen_ddl_datapilot.py                  # 输出所有表 DDL
    python3 gen_ddl_datapilot.py --table feat_a   # 只输出指定表
    python3 gen_ddl_datapilot.py --output ddl/    # 写入文件夹
"""

import argparse
import os
from config import (
    EVENT_CONFIG, WINDOWS_WITH_ALL, ALL_WINDOW, DIM_CONFIG, PAIR_CONFIG,
    feat_name,
)
from gen_hive_sql import _pair_alias

DEV_DB = "ec_risk_model_dev"


# ── 列类型推断 ───────────────────────────────────────────────────────────────

def _col(name: str, dtype: str, comment: str = "") -> str:
    c = f"    {name} {dtype}"
    if comment:
        c += f" COMMENT '{comment}'"
    return c


# ── feat_a 列清单（Dim1-4 + Dim5 simple）────────────────────────────────────

def _feat_a_cols() -> list[str]:
    cols = ["    loan_account_id STRING COMMENT '贷款账户ID'"]
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in WINDOWS_WITH_ALL:
            wl = "all" if w == ALL_WINDOW else f"{w}d"
            cols.append(_col(f"{a}_cnt_{wl}",       "BIGINT"))
            cols.append(_col(f"{a}_days_{wl}",      "BIGINT"))
            cols.append(_col(f"{a}_ever_{wl}",      "INT"))
            cols.append(_col(f"{a}_max_daily_{wl}", "BIGINT"))
        for w in WINDOWS_WITH_ALL:
            wl = "all" if w == ALL_WINDOW else f"{w}d"
            cols.append(_col(f"{a}_avg_daily_{wl}", "DOUBLE"))
            cols.append(_col(f"{a}_std_daily_{wl}", "DOUBLE"))
            cols.append(_col(f"{a}_cv_daily_{wl}",  "DOUBLE"))
            cols.append(_col(f"{a}_min_daily_{wl}", "BIGINT"))
        for w_s, w_l in DIM_CONFIG[3]["pairs"]:
            l_label = "all" if w_l == ALL_WINDOW else f"{w_l}d"
            cols.append(_col(f"{a}_ratio_{w_s}_{l_label}", "DOUBLE"))
        for p in DIM_CONFIG[4]["periods"]:
            cols.append(_col(feat_name(a, "delta",    p), "BIGINT"))
            cols.append(_col(feat_name(a, "chg_rate", p), "DOUBLE"))
            cols.append(_col(feat_name(a, "accel",    p), "INT"))
        cols.append(_col(feat_name(a, "days_since_last"),  "BIGINT"))
        cols.append(_col(feat_name(a, "days_since_first"), "BIGINT"))
    return cols


# ── feat_b 列清单（Dim5 complex）────────────────────────────────────────────

def _feat_b_cols() -> list[str]:
    cols = ["    loan_account_id STRING COMMENT '贷款账户ID'"]
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[5]["windowed"]["max_streak"]:
            cols.append(_col(feat_name(a, "max_streak",     w), "BIGINT"))
        for w in DIM_CONFIG[5]["windowed"]["max_gap"]:
            cols.append(_col(feat_name(a, "max_gap",        w), "BIGINT"))
        for w in DIM_CONFIG[5]["windowed"]["slope"]:
            cols.append(_col(feat_name(a, "slope",          w), "DOUBLE"))
        for w in DIM_CONFIG[5]["windowed"]["ewm"]:
            cols.append(_col(feat_name(a, "ewm",            w), "DOUBLE"))
        for w in DIM_CONFIG[5]["windowed"]["active_gap_avg"]:
            cols.append(_col(feat_name(a, "active_gap_avg", w), "DOUBLE"))
            cols.append(_col(feat_name(a, "active_gap_std", w), "DOUBLE"))
    return cols


# ── feat_c 列清单（Dim6 时间间隔）───────────────────────────────────────────

def _feat_c_cols() -> list[str]:
    cols = ["    loan_account_id STRING COMMENT '贷款账户ID'"]
    for ec, cfg in EVENT_CONFIG.items():
        a = cfg["alias"]
        for w in DIM_CONFIG[6]["windows"]:
            for agg in DIM_CONFIG[6]["aggs"]:
                cols.append(_col(feat_name(a, agg, w), "DOUBLE"))
    return cols


# ── feat_d 列清单（Dim7 A→B 序列）──────────────────────────────────────────

def _feat_d_cols() -> list[str]:
    cols = ["    loan_account_id STRING COMMENT '贷款账户ID'"]
    for ev_a, ev_b, _, _ in PAIR_CONFIG:
        pa = _pair_alias(ev_a, ev_b)
        cols.append(_col(f"{pa}_cnt_all",      "BIGINT"))
        cols.append(_col(f"{pa}_rate_all",     "DOUBLE"))
        cols.append(_col(f"{pa}_time_avg_all", "DOUBLE"))
        cols.append(_col(f"{pa}_time_min_all", "DOUBLE"))
        cols.append(_col(f"{pa}_rate_chg",     "DOUBLE"))
    return cols


# ── features 列清单（全量合并 + 跨事件比率）────────────────────────────────

def _features_cols() -> list[str]:
    from config import CROSS_RATIO_CONFIG
    cols = _feat_a_cols() + _feat_b_cols()[1:] + _feat_c_cols()[1:] + _feat_d_cols()[1:]
    for name, _num, _den in CROSS_RATIO_CONFIG:
        cols.append(_col(name, "DOUBLE"))
    return cols


# ── DDL 生成 ─────────────────────────────────────────────────────────────────

TABLE_DEFS = {
    "feat_a": {
        "table": "yz_event3_t1_feat_a",
        "comment": "埋点T+1特征 Job A（Dim1-4 基础/统计/比率/环比 + Dim5-simple）",
        "cols_fn": _feat_a_cols,
    },
    "feat_b": {
        "table": "yz_event3_t1_feat_b",
        "comment": "埋点T+1特征 Job B（Dim5-complex: streak/gap/slope/ewm/active_gap）",
        "cols_fn": _feat_b_cols,
    },
    "feat_c": {
        "table": "yz_event3_t1_feat_c",
        "comment": "埋点T+1特征 Job C（Dim6 时间间隔 intv_min/avg/max/std/cv）",
        "cols_fn": _feat_c_cols,
    },
    "feat_d": {
        "table": "yz_event3_t1_feat_d",
        "comment": "埋点T+1特征 Job D（Dim7 A→B 序列转化）",
        "cols_fn": _feat_d_cols,
    },
    "features": {
        "table": "yz_event3_t1_features",
        "comment": "埋点T+1特征宽表（全量合并，~8100列，按 loan_account_id × dt 粒度）",
        "cols_fn": _features_cols,
    },
}


def gen_ddl(table_key: str) -> str:
    td = TABLE_DEFS[table_key]
    cols = td["cols_fn"]()
    cols_sql = ",\n".join(cols)
    return (
        f"-- ===== {td['table']} =====\n"
        f"CREATE TABLE {DEV_DB}.{td['table']} (\n"
        f"{cols_sql}\n"
        f") COMMENT '{td['comment']}'\n"
        f"PARTITIONED BY (dt STRING COMMENT '任务运行日期，格式 yyyy-MM-dd');\n"
    )


def main():
    parser = argparse.ArgumentParser(description="生成宽表 DDL")
    parser.add_argument("--table", choices=list(TABLE_DEFS.keys()) + ["all"], default="all")
    parser.add_argument("--output", default=None, help="输出目录，不指定则打印到 stdout")
    args = parser.parse_args()

    tables = list(TABLE_DEFS.keys()) if args.table == "all" else [args.table]

    for t in tables:
        ddl = gen_ddl(t)
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            path = os.path.join(args.output, f"ddl_{t}.sql")
            with open(path, "w", encoding="utf-8") as f:
                f.write(ddl)
            td = TABLE_DEFS[t]
            n_cols = len(td["cols_fn"]())
            print(f"[OK] {t:12s} → {path}  ({n_cols:,d} cols)")
        else:
            print(ddl)


if __name__ == "__main__":
    main()
