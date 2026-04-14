################################### 温馨提示 ###################################
# 1. PySpark 每次执行都会从头开始执行完整的代码，不分段执行
from datapilot_spark_bootstrap import spark, DataPilotUtils
# ↑ 用于初始化 SparkSession, 以及在编辑器下方【结果】区域中输出 DataFrame, 请不要删除该引用！
###############################################################################

"""
埋点 T+1 Task 07 — Merge（合并 feat_a/b/c/d + 跨事件比率 → features）
目标表：ec_risk_model.yz_event3_t1_features  (~9,739 列)
依赖：Task03 + Task04 + Task05 + Task06 全部完成
"""

# ══════════════════════ 配置 ══════════════════════════════════════════════════

TABLE_FEAT_A     = "ec_risk_model.yz_event3_t1_feat_a"
TABLE_FEAT_B     = "ec_risk_model.yz_event3_t1_feat_b"
TABLE_FEAT_C     = "ec_risk_model.yz_event3_t1_feat_c"
TABLE_FEAT_D     = "ec_risk_model.yz_event3_t1_feat_d"
TABLE_FEAT_WRITE = "yz_event3_t1_features"

WINDOWS_WITH_ALL = [7, 14, 28, 56, 112, 224, "all"]
RATIO_PAIRS      = [(7, 14), (14, 28), (28, 56), (56, 112), (112, 224), (7, "all")]
DELTA_PERIODS    = [7, 14, 28, 56]

STREAK_WINDOWS     = [7, 28, 112, 224]
GAP_WINDOWS        = [7, 28, 112, 224]
SLOPE_WINDOWS      = [28, 112]
EWM_WINDOWS        = [7, 28]
ACTIVE_GAP_WINDOWS = [7, 28, 112, 224]

INTV_WINDOWS = [28, 112, 224, "all"]

# 65 个事件 alias 列表（顺序与 Task03-05 一致）
EVENT_CONFIG = {
    "auth_b553_pageview":            "authb553pageview",
    "auth_b553_d554_click":          "authb553d554click",
    "auth_b553_d555_click":          "authb553d555click",
    "auth_b560_d561_click":          "authb560d561click",
    "auth_b573_pageview":            "authb573pageview",
    "auth_b573_d574_click":          "authb573d574click",
    "auth_b573_d575_click":          "authb573d575click",
    "auth_b573_d585_click":          "authb573d585click",
    "auth_b578_pageview":            "authb578pageview",
    "auth_b578_d579_click":          "authb578d579click",
    "auth_b578_d580_click":          "authb578d580click",
    "auth_b578_c581_d582_click":     "authb578c581d582click",
    "auth_b594_pageview":            "authb594pageview",
    "auth_b594_d595_click":          "authb594d595click",
    "auth_b594_d596_click":          "authb594d596click",
    "auth_b594_d660_click":          "authb594d660click",
    "auth_b597_pageview":            "authb597pageview",
    "auth_b597_d598_click":          "authb597d598click",
    "auth_b603_pageview":            "authb603pageview",
    "auth_b603_d604_click":          "authb603d604click",
    "auth_b603_d605_click":          "authb603d605click",
    "auth_b606_pageview":            "authb606pageview",
    "auth_b606_d607_click":          "authb606d607click",
    "auth_b606_d608_click":          "authb606d608click",
    "auth_next_step_result":         "authnextstepresult",
    "loan_b1_pageview":              "loanb1pageview",
    "loan_b1_c140_click":            "loanb1c140click",
    "loan_b1_c145_click":            "loanb1c145click",
    "loan_b1_c148_exposure":         "loanb1c148exposure",
    "loan_b1_c148_d712_click":       "loanb1c148d712click",
    "loan_b1_c295_d711_click":       "loanb1c295d711click",
    "loan_b1_c2_click":              "loanb1c2click",
    "loan_b1_c41_d303_click":        "loanb1c41d303click",
    "loan_b1_c41_d304_click":        "loanb1c41d304click",
    "loan_b1_d709_click":            "loanb1d709click",
    "loan_b1_d73_click":             "loanb1d73click",
    "loan_first_pass_result":        "loanfirstpassresult",
    "loan_order_otp_code_result":    "loanorderotpcoderesult",
    "loan_orderbutton_click_result": "loanorderbuttonclickresult",
    "loan_orderpage_display_result": "loanorderpagedisplayresult",
    "loan_create_order_result":      "loancreateorderresult",
    "loan_create_order_check_result":"loancreateordercheckresult",
    "loan_enter_order_check_result": "loanenterordercheckresult",
    "loan_order_check_step_show_result": "loanordercheckstepshowresult",
    "loan_b79_c552_exposure":        "loanb79c552exposure",
    "login_b70_pageview":            "loginb70pageview",
    "login_b70_c732_d733_click":     "loginb70c732d733click",
    "login_b70_c154_d155_click":     "loginb70c154d155click",
    "login_b70_c154_d156_click":     "loginb70c154d156click",
    "login_b269_pageview":           "loginb269pageview",
    "login_b269_d270_click":         "loginb269d270click",
    "login_b269_d271_click":         "loginb269d271click",
    "login_b222_c233_click":         "loginb222c233click",
    "login_login_result":            "loginloginresult",
    "login_register_result":         "loginregisterresult",
    "login_message_authorization_popup_result": "loginmessageauthorizationpopupresult",
    "general_switch_in_result":      "generalswitchinresult",
    "general_switch_out_result":     "generalswitchoutresult",
    "general_b718_pageview":         "generalb718pageview",
    "general_b396_pageview":         "generalb396pageview",
    "post_repayment_result":         "postrepaymentresult",
    "post_b131_c134_d135_click":     "postb131c134d135click",
    "AppStart":                      "appstart",
    "AppEnd":                        "append",
    "other_b646_pageview":           "otherb646pageview",
}

# Dim7 事件对 alias（与 Task06 一致）
PAIR_ALIASES = [
    ("authb553pageview",        "authb553d554click"),
    ("authb553pageview",        "authb553d555click"),
    ("authb573pageview",        "authb573d574click"),
    ("authb573pageview",        "authb594pageview"),
    ("authb594pageview",        "authb597pageview"),
    ("authb597pageview",        "authb606pageview"),
    ("authb573pageview",        "authb606pageview"),
    ("authb594pageview",        "authb573pageview"),
    ("loanb1pageview",          "loanb1d709click"),
    ("loanb1pageview",          "loanorderbuttonclickresult"),
    ("loanb1c41d303click",      "loanb1d709click"),
    ("loanorderpagedisplayresult", "loanorderbuttonclickresult"),
    ("loanorderbuttonclickresult", "loanorderotpcoderesult"),
    ("loanorderotpcoderesult",  "loancreateorderresult"),
    ("loanfirstpassresult",     "loanb1pageview"),
    ("postb131c134d135click",   "postrepaymentresult"),
    ("postrepaymentresult",     "loanb1pageview"),
    ("loginloginresult",        "loanb1pageview"),
]

# 19 个跨事件比率 (name, numerator_col_in_a, denominator_expr)
CROSS_RATIO_CONFIG = [
    ("auth_retain_net_rate_all",
     "authb553d554click_cnt_all",
     "NULLIF(a.authb553d554click_cnt_all+a.authb553d555click_cnt_all,0)"),
    ("ktp_shoot_rate_all",
     "authb573d574click_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all,0)"),
    ("ktp_to_lv_rate_all",
     "authb597pageview_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all,0)"),
    ("ktp_to_bind_rate_all",
     "authb606pageview_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all,0)"),
    ("ktp_exit_rate_all",
     "authb573d585click_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all,0)"),
    ("ktp_retry_rate_all",
     "authb594pageview_cnt_all",
     "NULLIF(a.authb573pageview_cnt_all,0)"),
    ("lv_shoot_rate_all",
     "authb597d598click_cnt_all",
     "NULLIF(a.authb597pageview_cnt_all,0)"),
    ("switch_ratio_7d",
     "generalswitchoutresult_cnt_7d",
     "NULLIF(a.generalswitchinresult_cnt_7d,0)"),
    ("b1_apply_rate_28d",
     "loanb1d709click_cnt_28d",
     "NULLIF(a.loanb1pageview_cnt_28d,0)"),
    ("b1_confirm_rate_28d",
     "loanb1d73click_cnt_28d",
     "NULLIF(a.loanb1d709click_cnt_28d,0)"),
    ("b1_adjust_rate_28d",
     "loanb1c41d303click_cnt_28d",
     "NULLIF(a.loanb1pageview_cnt_28d,0)"),
    ("b1_exposure_rate_28d",
     "loanb1c148exposure_cnt_28d",
     "NULLIF(a.loanb1pageview_cnt_28d,0)"),
    ("repay_recent_ratio_7_all",
     "postrepaymentresult_cnt_7d",
     "NULLIF(a.postrepaymentresult_cnt_all,0)"),
    ("repay_recent_ratio_28_all",
     "postrepaymentresult_cnt_28d",
     "NULLIF(a.postrepaymentresult_cnt_all,0)"),
    ("repay_recent_ratio_112_all",
     "postrepaymentresult_cnt_112d",
     "NULLIF(a.postrepaymentresult_cnt_all,0)"),
    ("repay_click_to_result_28d",
     "postb131c134d135click_cnt_28d",
     "NULLIF(a.postrepaymentresult_cnt_28d,0)"),
    ("login_to_loan_ratio_7d",
     "loanb1pageview_cnt_7d",
     "NULLIF(a.loginloginresult_cnt_7d,0)"),
    ("login_to_loan_ratio_28d",
     "loanb1pageview_cnt_28d",
     "NULLIF(a.loginloginresult_cnt_28d,0)"),
    ("switch_ratio_28d",
     "generalswitchoutresult_cnt_28d",
     "NULLIF(a.generalswitchinresult_cnt_28d,0)"),
]

# ══════════════════════ 列名收集 ══════════════════════════════════════════════

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

# ══════════════════════ SQL 生成 ══════════════════════════════════════════════

def sql_merge(dt: str) -> str:
    all_cols = (
        [f"    ,{c}" for c in _collect_a()]
        + [f"    ,{c}" for c in _collect_b()]
        + [f"    ,{c}" for c in _collect_c()]
        + [f"    ,{c}" for c in _collect_d()]
        + [f"    ,{c}" for c in _cross_ratio_cols()]
    )
    return f"""
INSERT OVERWRITE TABLE {TABLE_FEAT_WRITE}
    PARTITION(dt = '{dt}')
SELECT
    a.loan_account_id
{chr(10).join(all_cols)}
FROM {TABLE_FEAT_A} a
LEFT JOIN {TABLE_FEAT_B} b ON a.loan_account_id = b.loan_account_id AND b.dt = '{dt}'
LEFT JOIN {TABLE_FEAT_C} c ON a.loan_account_id = c.loan_account_id AND c.dt = '{dt}'
LEFT JOIN {TABLE_FEAT_D} d ON a.loan_account_id = d.loan_account_id AND d.dt = '{dt}'
WHERE a.dt = '{dt}';
"""

# ══════════════════════ 执行 ══════════════════════════════════════════════════

def process_logic():
    dt = "${p_date_iso}"
    spark.sql(sql_merge(dt))

if __name__ == "__main__":
    dt = "${p_date_iso}"
    print(f"[Task07] merge 开始，dt={dt}")
    process_logic()
    spark.stop()
    print("[Task07] merge 完成")
