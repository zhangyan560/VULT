"""
埋点 T+1 定时任务 — DataPilot 迁移配置

仅覆盖 TABLE 字典（读取加 ec_risk_model. 前缀，写入不加前缀）。
事件配置、维度配置、窗口配置等全部继承 config.py，保持业务语义不变。
"""

# ── 继承原始配置（事件池 / 维度 / 窗口 / 事件对 / 跨事件比率）──────────────
from config import (                                                   # noqa: F401,F403
    WINDOWS, ALL_WINDOW, WINDOWS_WITH_ALL, MAX_LOOKBACK_DAYS,
    EVENT_CONFIG, ALL_EVENTS, ALL_ALIASES,
    DIM_CONFIG, PAIR_CONFIG, PAIR_EVENTS,
    CROSS_RATIO_CONFIG, BASE_TABLE_RISK_TYPES,
    event_in_clause, window_cond, feat_name,
)

# ── 覆盖 TABLE：读取走 ec_risk_model. 前缀，写入不加前缀 ─────────────────────
#   DataPilot 规范：写入表名不带库前缀，平台按任务保存路径自动路由

TABLE = {
    # 人群 base 表
    "base":             "ec_risk_model.yz_event3_t1_base",
    "base_write":       "yz_event3_t1_base",

    # 每日计数中间层
    "daily_cnt":        "ec_risk_model.yz_event3_t1_daily_cnt",
    "daily_cnt_write":  "yz_event3_t1_daily_cnt",

    # 源数据（保持原始库前缀）
    "event_log":        "ec_dwd.dwd_ec_log_di_sa_app_events",
    "underwrite":       "dm_id.dm_id_risk_df_underwrite",

    # Job 中间宽表（各 Job 独立写入，merge 读取）
    "feat_a":           "ec_risk_model.yz_event3_t1_feat_a",
    "feat_a_write":     "yz_event3_t1_feat_a",
    "feat_b":           "ec_risk_model.yz_event3_t1_feat_b",
    "feat_b_write":     "yz_event3_t1_feat_b",
    "feat_c":           "ec_risk_model.yz_event3_t1_feat_c",
    "feat_c_write":     "yz_event3_t1_feat_c",
    "feat_d":           "ec_risk_model.yz_event3_t1_feat_d",
    "feat_d_write":     "yz_event3_t1_feat_d",

    # 最终特征宽表
    "features":         "ec_risk_model.yz_event3_t1_features",
    "features_write":   "yz_event3_t1_features",
}
