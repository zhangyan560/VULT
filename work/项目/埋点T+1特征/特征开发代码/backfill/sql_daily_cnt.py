"""
Step 0: 从原始 event_log 计算 daily_cnt（每用户每事件每天的次数）

定时任务的 yz_event3_t1_daily_cnt 不适用于回溯（只有当天分区）。
回溯需从 ec_dwd.dwd_ec_log_di_sa_app_events 直接聚合，
人群限定为 trace 表中的 loan_account_id，日期覆盖 [min_anchor-224, max_anchor)。

输出表：{output_prefix}_daily_cnt
  loan_account_id STRING
  event_code      STRING
  event_date      STRING  (yyyy-MM-dd)
  daily_cnt       BIGINT
"""

from config import EVENT_CONFIG, TABLE_EVENT_LOG, MAX_LOOKBACK_DAYS

def _event_in_clause():
    return "(" + ",".join(f"'{e}'" for e in EVENT_CONFIG) + ")"

def sql_daily_cnt(trace_table: str, output_prefix: str, min_anchor: str, max_anchor: str) -> str:
    """
    trace_table   : 人群表，需含 loan_account_id
    output_prefix : 输出前缀，写入 {output_prefix}_daily_cnt
    min_anchor    : yyyy-MM-dd，最早锚点
    max_anchor    : yyyy-MM-dd，最晚锚点（不含）
    """
    table_write = f"{output_prefix}_daily_cnt"
    # dt 分区格式 yyyyMMdd，多留 1 天缓冲
    return f"""
CREATE TABLE {table_write} AS
WITH pop AS (
    SELECT DISTINCT loan_account_id
    FROM {trace_table}
)
SELECT
    e.loan_account_id,
    e.event_code,
    TO_DATE(e.created_date) AS event_date,
    COUNT(*)                AS daily_cnt
FROM {TABLE_EVENT_LOG} e
INNER JOIN pop ON e.loan_account_id = pop.loan_account_id
WHERE e.dt >= REGEXP_REPLACE(CAST(DATE_SUB('{min_anchor}', {MAX_LOOKBACK_DAYS + 1}) AS STRING), '-', '')
  AND e.dt <  REGEXP_REPLACE('{max_anchor}', '-', '')
  AND e.event_code IN {_event_in_clause()}
  AND e.loan_account_id IS NOT NULL
GROUP BY e.loan_account_id, e.event_code, TO_DATE(e.created_date)
"""
