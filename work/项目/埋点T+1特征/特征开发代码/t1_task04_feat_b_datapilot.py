################################### 温馨提示 ###################################
# 1. PySpark 每次执行都会从头开始执行完整的代码，不分段执行
from datapilot_spark_bootstrap import spark, DataPilotUtils
# ↑ 用于初始化 SparkSession, 以及在编辑器下方【结果】区域中输出 DataFrame, 请不要删除该引用！
###############################################################################

"""
埋点 T+1 Task 04 — feat_b（Dim5 complex: streak/gap/slope/ewm/active_gap）
目标表：ec_risk_model.yz_event3_t1_feat_b  (~1,430 列)
依赖：Task01(base) + Task02(daily_cnt)
"""

# ══════════════════════ 配置 ══════════════════════════════════════════════════

TABLE_BASE       = "ec_risk_model.yz_event3_t1_base"
TABLE_DAILY      = "ec_risk_model.yz_event3_t1_daily_cnt"
TABLE_FEAT_WRITE = "yz_event3_t1_feat_b"

MAX_LOOKBACK_DAYS = 224

# Dim5 窗口配置
STREAK_WINDOWS    = [7, 28, 112, 224]
GAP_WINDOWS       = [7, 28, 112, 224]
SLOPE_WINDOWS     = [28, 112]
EWM_WINDOWS       = [7, 28]
ACTIVE_GAP_WINDOWS = [7, 28, 112, 224]

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

def _fn(alias, agg, w=None):
    if w is None:
        return f"{alias}_{agg}"
    return f"{alias}_{agg}_{w}d"

def _wc_days(col, w):
    return f"{col} BETWEEN 1 AND {w}"

# ── Dim5 complex 列生成 ───────────────────────────────────────────────────
def _streak_gap_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in STREAK_WINDOWS:
            cols.append(f"    ,MAX(CASE WHEN sl.event_code='{ec}' AND streak_min_db <= {w} THEN sl.streak_length END) AS {_fn(a,'max_streak',w)}")
        for w in GAP_WINDOWS:
            cols.append(f"    ,MAX(CASE WHEN ds.event_code='{ec}' AND {_wc_days('ds.days_back',w)} AND ds.gap_days IS NOT NULL THEN ds.gap_days END) AS {_fn(a,'max_gap',w)}")
    return cols

def _slope_cols():
    cols = []
    for ec, a in EVENT_CONFIG.items():
        for w in SLOPE_WINDOWS:
            wc = _wc_days("ds.days_back", w)
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

# ══════════════════════ SQL 生成 ══════════════════════════════════════════════

def sql_feat_b(dt: str) -> str:
    anchor = f"'{dt}'"
    all_cols = _streak_gap_cols() + _slope_cols() + _ewm_cols() + _active_gap_cols()
    return f"""
INSERT OVERWRITE TABLE {TABLE_FEAT_WRITE}
    PARTITION(dt = '{dt}')
WITH day_seq AS (
    SELECT
        d.loan_account_id,
        d.event_code,
        d.event_date,
        d.daily_cnt,
        DATEDIFF({anchor}, d.event_date) AS days_back,
        DATEDIFF(d.event_date,
            LAG(d.event_date) OVER (
                PARTITION BY d.loan_account_id, d.event_code ORDER BY d.event_date
            )) AS gap_days
    FROM {TABLE_DAILY} d
    INNER JOIN {TABLE_BASE} b
        ON d.loan_account_id = b.loan_account_id AND b.dt = '{dt}'
    WHERE d.event_date >= DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS})
      AND d.event_date < {anchor}
      AND d.daily_cnt > 0
),
streak_calc AS (
    SELECT loan_account_id, event_code, event_date, days_back,
           DATEDIFF(event_date, '1970-01-01') - ROW_NUMBER() OVER (
               PARTITION BY loan_account_id, event_code ORDER BY event_date
           ) AS streak_grp
    FROM day_seq
),
streak_len AS (
    SELECT loan_account_id, event_code, streak_grp,
           MIN(days_back) AS streak_min_db,
           COUNT(*)       AS streak_length
    FROM streak_calc
    GROUP BY loan_account_id, event_code, streak_grp
)
SELECT
    COALESCE(sl.loan_account_id, ds.loan_account_id) AS loan_account_id
{chr(10).join(all_cols)}
FROM (SELECT DISTINCT loan_account_id FROM day_seq) uid
LEFT JOIN streak_len sl ON uid.loan_account_id = sl.loan_account_id
LEFT JOIN day_seq    ds ON uid.loan_account_id = ds.loan_account_id
GROUP BY COALESCE(sl.loan_account_id, ds.loan_account_id);
"""

# ══════════════════════ 执行 ══════════════════════════════════════════════════

def process_logic():
    dt = "${p_date_iso}"
    spark.sql(sql_feat_b(dt))

if __name__ == "__main__":
    dt = "${p_date_iso}"
    print(f"[Task04] feat_b 开始，dt={dt}")
    process_logic()
    spark.stop()
    print("[Task04] feat_b 完成")
