################################### 温馨提示 ###################################
# 1. PySpark 每次执行都会从头开始执行完整的代码，不分段执行
from datapilot_spark_bootstrap import spark, DataPilotUtils
# ↑ 用于初始化 SparkSession, 以及在编辑器下方【结果】区域中输出 DataFrame, 请不要删除该引用！
###############################################################################

"""
埋点 T+1 Task 05 — feat_c（Dim6 时间间隔）
目标表：ec_risk_model.yz_event3_t1_feat_c  (~1,300 列)
依赖：Task01(base)，直接读 event_log 原始日志
"""

# ══════════════════════ 配置 ══════════════════════════════════════════════════

TABLE_BASE       = "ec_risk_model.yz_event3_t1_base"
TABLE_EVENT_LOG  = "ec_dwd.dwd_ec_log_di_sa_app_events"
TABLE_FEAT_WRITE = "yz_event3_t1_feat_c"

MAX_LOOKBACK_DAYS = 224

# Dim6 窗口（天）
INTV_WINDOWS = [28, 112, 224, "all"]

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

# ══════════════════════ 列生成工具 ════════════════════════════════════════════

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

# ══════════════════════ SQL 生成 ══════════════════════════════════════════════

def sql_feat_c(dt: str) -> str:
    anchor = f"'{dt}'"
    return f"""
INSERT OVERWRITE TABLE {TABLE_FEAT_WRITE}
    PARTITION(dt = '{dt}')
WITH evt AS (
    SELECT
        e.loan_account_id,
        e.event_code,
        e.created_date,
        DATEDIFF({anchor}, TO_DATE(e.created_date)) AS days_back,
        LAG(e.created_date) OVER (
            PARTITION BY e.loan_account_id, e.event_code ORDER BY e.created_date
        ) AS prev_created_date
    FROM {TABLE_EVENT_LOG} e
    INNER JOIN {TABLE_BASE} b
        ON e.loan_account_id = b.loan_account_id
        AND e.user_id = b.user_id
        AND b.dt = '{dt}'
    WHERE e.dt >= REGEXP_REPLACE(CAST(DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS + 1}) AS STRING), '-', '')
      AND e.event_code IN {_event_in_clause()}
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
{chr(10).join(_dim6_cols())}
FROM itv
GROUP BY loan_account_id;
"""

# ══════════════════════ 执行 ══════════════════════════════════════════════════

def process_logic():
    dt = "${p_date_iso}"
    spark.sql(sql_feat_c(dt))

if __name__ == "__main__":
    dt = "${p_date_iso}"
    print(f"[Task05] feat_c 开始，dt={dt}")
    process_logic()
    spark.stop()
    print("[Task05] feat_c 完成")
