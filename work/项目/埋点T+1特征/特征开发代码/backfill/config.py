"""
离线回溯共享配置
所有 sql_feat_*.py 和 sql_merge.py 从此处 import。
"""

# ── 数据源表 ───────────────────────────────────────────────────────────────
# 回溯 daily_cnt 由 sql_daily_cnt.py 从 event_log 现算，不使用定时任务的 yz_event3_t1_daily_cnt
TABLE_EVENT_LOG = "ec_dwd.dwd_ec_log_di_sa_app_events"

MAX_LOOKBACK_DAYS = 224

# ── 窗口配置 ───────────────────────────────────────────────────────────────
WINDOWS          = [7, 14, 28, 56, 112, 224]
ALL_WINDOW       = "all"
WINDOWS_WITH_ALL = WINDOWS + [ALL_WINDOW]

RATIO_PAIRS   = [(7, 14), (14, 28), (28, 56), (56, 112), (112, 224), (7, "all")]
DELTA_PERIODS = [7, 14, 28, 56]

STREAK_WINDOWS     = [7, 28, 112, 224]
GAP_WINDOWS        = [7, 28, 112, 224]
SLOPE_WINDOWS      = [28, 112]
EWM_WINDOWS        = [7, 28]
ACTIVE_GAP_WINDOWS = [7, 28, 112, 224]

INTV_WINDOWS = [28, 112, 224, "all"]

# ── 65 个事件 {event_code: alias} ─────────────────────────────────────────
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

# ── feat_d 所用事件 alias（子集）──────────────────────────────────────────
EVENT_ALIAS = {
    "auth_b553_pageview":            "authb553pageview",
    "auth_b553_d554_click":          "authb553d554click",
    "auth_b553_d555_click":          "authb553d555click",
    "auth_b573_pageview":            "authb573pageview",
    "auth_b573_d574_click":          "authb573d574click",
    "auth_b594_pageview":            "authb594pageview",
    "auth_b597_pageview":            "authb597pageview",
    "auth_b606_pageview":            "authb606pageview",
    "loan_b1_pageview":              "loanb1pageview",
    "loan_b1_d709_click":            "loanb1d709click",
    "loan_b1_c41_d303_click":        "loanb1c41d303click",
    "loan_orderpage_display_result": "loanorderpagedisplayresult",
    "loan_orderbutton_click_result": "loanorderbuttonclickresult",
    "loan_order_otp_code_result":    "loanorderotpcoderesult",
    "loan_create_order_result":      "loancreateorderresult",
    "loan_first_pass_result":        "loanfirstpassresult",
    "post_b131_c134_d135_click":     "postb131c134d135click",
    "post_repayment_result":         "postrepaymentresult",
    "login_login_result":            "loginloginresult",
}

# ── Dim7 事件对 (event_A, event_B, window_hours) ──────────────────────────
PAIR_CONFIG = [
    ("auth_b553_pageview",           "auth_b553_d554_click",          1),
    ("auth_b553_pageview",           "auth_b553_d555_click",          1),
    ("auth_b573_pageview",           "auth_b573_d574_click",          0.17),
    ("auth_b573_pageview",           "auth_b594_pageview",            0.5),
    ("auth_b594_pageview",           "auth_b597_pageview",            48),
    ("auth_b597_pageview",           "auth_b606_pageview",            48),
    ("auth_b573_pageview",           "auth_b606_pageview",            72),
    ("auth_b594_pageview",           "auth_b573_pageview",            1),
    ("loan_b1_pageview",             "loan_b1_d709_click",            24),
    ("loan_b1_pageview",             "loan_orderbutton_click_result", 24),
    ("loan_b1_c41_d303_click",       "loan_b1_d709_click",            1),
    ("loan_orderpage_display_result","loan_orderbutton_click_result", 1),
    ("loan_orderbutton_click_result","loan_order_otp_code_result",    0.17),
    ("loan_order_otp_code_result",   "loan_create_order_result",      0.17),
    ("loan_first_pass_result",       "loan_b1_pageview",              168),
    ("post_b131_c134_d135_click",    "post_repayment_result",         1),
    ("post_repayment_result",        "loan_b1_pageview",              168),
    ("login_login_result",           "loan_b1_pageview",              1),
]

# ── merge 用：pair alias 元组列表 ─────────────────────────────────────────
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

# ── 跨事件比率（19 个）────────────────────────────────────────────────────
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
