################################### 温馨提示 ###################################
# 1. PySpark 每次执行都会从头开始执行完整的代码，不分段执行
from datapilot_spark_bootstrap import spark, DataPilotUtils
# ↑ 用于初始化 SparkSession, 以及在编辑器下方【结果】区域中输出 DataFrame, 请不要删除该引用！
###############################################################################

"""
埋点 T+1 Task 06 — feat_d（Dim7 A→B 序列模式）
目标表：ec_risk_model.yz_event3_t1_feat_d  (~90 列)
依赖：Task01(base)，直接读 event_log 原始日志
"""

# ══════════════════════ 配置 ══════════════════════════════════════════════════

TABLE_BASE       = "ec_risk_model.yz_event3_t1_base"
TABLE_EVENT_LOG  = "ec_dwd.dwd_ec_log_di_sa_app_events"
TABLE_FEAT_WRITE = "yz_event3_t1_feat_d"

MAX_LOOKBACK_DAYS = 224

# event_code → alias
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

# (event_A, event_B, window_hours)
PAIR_CONFIG = [
    ("auth_b553_pageview",           "auth_b553_d554_click",          1),      # P1
    ("auth_b553_pageview",           "auth_b553_d555_click",          1),      # P2
    ("auth_b573_pageview",           "auth_b573_d574_click",          0.17),   # P3
    ("auth_b573_pageview",           "auth_b594_pageview",            0.5),    # P4
    ("auth_b594_pageview",           "auth_b597_pageview",            48),     # P5
    ("auth_b597_pageview",           "auth_b606_pageview",            48),     # P6
    ("auth_b573_pageview",           "auth_b606_pageview",            72),     # P7
    ("auth_b594_pageview",           "auth_b573_pageview",            1),      # P8
    ("loan_b1_pageview",             "loan_b1_d709_click",            24),     # P9
    ("loan_b1_pageview",             "loan_orderbutton_click_result", 24),     # P10
    ("loan_b1_c41_d303_click",       "loan_b1_d709_click",            1),      # P11
    ("loan_orderpage_display_result","loan_orderbutton_click_result", 1),      # P12
    ("loan_orderbutton_click_result","loan_order_otp_code_result",    0.17),   # P13
    ("loan_order_otp_code_result",   "loan_create_order_result",      0.17),   # P14
    ("loan_first_pass_result",       "loan_b1_pageview",              168),    # P15
    ("post_b131_c134_d135_click",    "post_repayment_result",         1),      # P16
    ("post_repayment_result",        "loan_b1_pageview",              168),    # P17
    ("login_login_result",           "loan_b1_pageview",              1),      # P18
]

PAIR_EVENTS = list(dict.fromkeys(
    [a for a, _, _ in PAIR_CONFIG] + [b for _, b, _ in PAIR_CONFIG]
))

# ══════════════════════ SQL 生成 ══════════════════════════════════════════════

def _pair_alias(ev_a, ev_b):
    return f"{EVENT_ALIAS[ev_a]}_to_{EVENT_ALIAS[ev_b]}"

def _event_in_clause(events):
    return "(" + ",".join(f"'{e}'" for e in events) + ")"

def sql_feat_d(dt: str) -> str:
    anchor = f"'{dt}'"

    pair_ctes = []
    pair_selects = []

    for idx, (ev_a, ev_b, win_h) in enumerate(PAIR_CONFIG):
        pname = f"p{idx}"
        pa = _pair_alias(ev_a, ev_b)
        win_sec = int(win_h * 3600)

        pair_ctes.append(f"""{pname} AS (
    SELECT
        a.loan_account_id,
        a.created_date AS a_time,
        MIN(CASE
            WHEN b.event_code = '{ev_b}'
             AND b.created_date > a.created_date
             AND (UNIX_TIMESTAMP(b.created_date) - UNIX_TIMESTAMP(a.created_date)) <= {win_sec}
            THEN b.created_date
        END) AS first_b_time
    FROM evt_filtered a
    LEFT JOIN evt_filtered b ON a.loan_account_id = b.loan_account_id
    WHERE a.event_code = '{ev_a}'
    GROUP BY a.loan_account_id, a.created_date
)""")

        pair_selects.append(f"""
    ,COUNT({pname}.a_time) AS {pa}_cnt_all
    ,SUM(CASE WHEN {pname}.first_b_time IS NOT NULL THEN 1 ELSE 0 END)*1.0
        /NULLIF(COUNT({pname}.a_time),0) AS {pa}_rate_all
    ,AVG(CASE WHEN {pname}.first_b_time IS NOT NULL
        THEN (UNIX_TIMESTAMP({pname}.first_b_time)-UNIX_TIMESTAMP({pname}.a_time))/3600.0 END) AS {pa}_time_avg_all
    ,MIN(CASE WHEN {pname}.first_b_time IS NOT NULL
        THEN (UNIX_TIMESTAMP({pname}.first_b_time)-UNIX_TIMESTAMP({pname}.a_time))/3600.0 END) AS {pa}_time_min_all
    ,NULL AS {pa}_rate_chg""")

    left_joins = "\n".join(
        f"LEFT JOIN p{i} ON uid.loan_account_id = p{i}.loan_account_id"
        for i in range(len(PAIR_CONFIG))
    )

    return f"""
INSERT OVERWRITE TABLE {TABLE_FEAT_WRITE}
    PARTITION(dt = '{dt}')
WITH evt_filtered AS (
    SELECT e.loan_account_id, e.event_code, e.created_date
    FROM {TABLE_EVENT_LOG} e
    INNER JOIN {TABLE_BASE} b
        ON e.loan_account_id = b.loan_account_id
        AND e.user_id = b.user_id
        AND b.dt = '{dt}'
    WHERE e.dt >= REGEXP_REPLACE(CAST(DATE_SUB({anchor}, {MAX_LOOKBACK_DAYS + 1}) AS STRING), '-', '')
      AND e.event_code IN {_event_in_clause(PAIR_EVENTS)}
      AND e.loan_account_id IS NOT NULL
      AND TO_DATE(e.created_date) < {anchor}
),
uid AS (SELECT DISTINCT loan_account_id FROM evt_filtered),
{",".join(pair_ctes)}
SELECT
    uid.loan_account_id
{"".join(pair_selects)}
FROM uid
{left_joins}
GROUP BY uid.loan_account_id;
"""

# ══════════════════════ 执行 ══════════════════════════════════════════════════

def process_logic():
    dt = "${p_date_iso}"
    spark.sql(sql_feat_d(dt))

if __name__ == "__main__":
    dt = "${p_date_iso}"
    print(f"[Task06] feat_d 开始，dt={dt}")
    process_logic()
    spark.stop()
    print("[Task06] feat_d 完成")
