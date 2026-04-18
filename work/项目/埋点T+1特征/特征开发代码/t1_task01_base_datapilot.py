################################### 温馨提示 ###################################
# 1. PySpark 每次执行都会从头开始执行完整的代码，不分段执行
from datapilot_spark_bootstrap import spark, DataPilotUtils
# ↑ 用于初始化 SparkSession, 以及在编辑器下方【结果】区域中输出 DataFrame, 请不要删除该引用！
###############################################################################

"""
埋点 T+1 Task 01 — 人群 base 表
目标表：ec_risk_model.yz_event3_t1_base
分区键：dt (yyyy-MM-dd) 每日全量覆写
依赖：dm_id.dm_id_risk_df_underwrite
"""

# ── 配置 ───────────────────────────────────────────────────────────────────
BASE_TABLE_WRITE   = "yz_event3_t1_base"
TABLE_UNDERWRITE   = "dm_id.dm_id_risk_df_underwrite"
BASE_TABLE_RISK_TYPES = (
    "'首贷还款续借','复贷还款续借','复贷打款续借','结清复贷',"
    "'循环贷','首贷风控','首贷回捞'"
)

# ── SQL ────────────────────────────────────────────────────────────────────
def sql_base_table(dt: str) -> str:
    return f"""
INSERT OVERWRITE TABLE {BASE_TABLE_WRITE}
    PARTITION(dt = '{dt}')
SELECT DISTINCT
    loan_account_id,
    user_id
FROM {TABLE_UNDERWRITE}
WHERE from_unixtime(bigint(trace_created_ts/1000)-3600, 'yyyy-MM-dd') >= '2025-01-01'
  AND trace_risk_type_name IN ({BASE_TABLE_RISK_TYPES})
  AND dt = date_format(date_sub('{dt}', 1), 'yyyyMMdd');
"""

# ── 执行 ───────────────────────────────────────────────────────────────────
def process_logic():
    dt = "${p_date_iso}"
    spark.sql(sql_base_table(dt))

if __name__ == "__main__":
    dt = "${p_date_iso}"
    print(f"[Task01] base 表开始，dt={dt}")
    process_logic()
    spark.stop()
    print("[Task01] base 表完成")
