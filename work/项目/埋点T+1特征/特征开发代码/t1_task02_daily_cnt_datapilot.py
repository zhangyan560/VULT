################################### 温馨提示 ###################################
# 1. PySpark 每次执行都会从头开始执行完整的代码，不分段执行
from datapilot_spark_bootstrap import spark, DataPilotUtils
# ↑ 用于初始化 SparkSession, 以及在编辑器下方【结果】区域中输出 DataFrame, 请不要删除该引用！
###############################################################################

"""
埋点 T+1 Task 02 — daily_cnt 每日增量计数
目标表：ec_risk_model.yz_event3_t1_daily_cnt
分区键：event_date (yyyy-MM-dd)
迁移变更：原脚本刷新最近3天分区，DataPilot 改为只写当天分区（单 INSERT 限制）。
"""

# ── 65 个目标事件 ──────────────────────────────────────────────────────────
ALL_EVENTS = [
    # auth 认证类（25个）
    "auth_b553_pageview", "auth_b553_d554_click", "auth_b553_d555_click",
    "auth_b560_d561_click", "auth_b573_pageview", "auth_b573_d574_click",
    "auth_b573_d575_click", "auth_b573_d585_click", "auth_b578_pageview",
    "auth_b578_d579_click", "auth_b578_d580_click", "auth_b578_c581_d582_click",
    "auth_b594_pageview", "auth_b594_d595_click", "auth_b594_d596_click",
    "auth_b594_d660_click", "auth_b597_pageview", "auth_b597_d598_click",
    "auth_b603_pageview", "auth_b603_d604_click", "auth_b603_d605_click",
    "auth_b606_pageview", "auth_b606_d607_click", "auth_b606_d608_click",
    "auth_next_step_result",
    # loan_b1 贷款主页类（12个）
    "loan_b1_pageview", "loan_b1_c140_click", "loan_b1_c145_click",
    "loan_b1_c148_exposure", "loan_b1_c148_d712_click", "loan_b1_c295_d711_click",
    "loan_b1_c2_click", "loan_b1_c41_d303_click", "loan_b1_c41_d304_click",
    "loan_b1_d709_click", "loan_b1_d73_click", "loan_first_pass_result",
    # loan_order 申请流程类（8个）
    "loan_order_otp_code_result", "loan_orderbutton_click_result",
    "loan_orderpage_display_result", "loan_create_order_result",
    "loan_create_order_check_result", "loan_enter_order_check_result",
    "loan_order_check_step_show_result", "loan_b79_c552_exposure",
    # login 登录注册类（11个）
    "login_b70_pageview", "login_b70_c732_d733_click", "login_b70_c154_d155_click",
    "login_b70_c154_d156_click", "login_b269_pageview", "login_b269_d270_click",
    "login_b269_d271_click", "login_b222_c233_click", "login_login_result",
    "login_register_result", "login_message_authorization_popup_result",
    # general 通用类（4个）
    "general_switch_in_result", "general_switch_out_result",
    "general_b718_pageview", "general_b396_pageview",
    # post 还款类（2个）
    "post_repayment_result", "post_b131_c134_d135_click",
    # App 生命周期（2个）
    "AppStart", "AppEnd",
    # 其他（1个）
    "other_b646_pageview",
]

TABLE_EVENT_LOG    = "ec_dwd.dwd_ec_log_di_sa_app_events"
TABLE_DAILY_WRITE  = "yz_event3_t1_daily_cnt"

def _event_in_clause():
    return "(" + ",".join(f"'{e}'" for e in ALL_EVENTS) + ")"

# ── SQL ────────────────────────────────────────────────────────────────────
def sql_daily_cnt(dt: str) -> str:
    return f"""
INSERT OVERWRITE TABLE {TABLE_DAILY_WRITE}
    PARTITION(event_date = '{dt}')
SELECT
    loan_account_id,
    event_code,
    CAST(COUNT(*) AS INT)                AS daily_cnt,
    COALESCE(SUM(event_duration), 0)     AS daily_dur_sum,
    COALESCE(MAX(event_duration), 0)     AS daily_dur_max
FROM {TABLE_EVENT_LOG}
WHERE dt = REGEXP_REPLACE('{dt}', '-', '')
  AND event_code IN {_event_in_clause()}
  AND loan_account_id IS NOT NULL
GROUP BY loan_account_id, event_code;
"""

# ── 执行 ───────────────────────────────────────────────────────────────────
def process_logic():
    dt = "${p_date_iso}"
    spark.sql(sql_daily_cnt(dt))

if __name__ == "__main__":
    dt = "${p_date_iso}"
    print(f"[Task02] daily_cnt 开始，event_date={dt}")
    process_logic()
    spark.stop()
    print("[Task02] daily_cnt 完成")
