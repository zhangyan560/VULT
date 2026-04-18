-- ===== yz_event3_t1_base =====
CREATE TABLE ec_risk_model_dev.yz_event3_t1_base (
    loan_account_id STRING COMMENT '贷款账户ID',
    user_id         STRING COMMENT '用户ID'
) COMMENT '埋点T+1特征 人群base表，每日全量覆写'
PARTITIONED BY (dt STRING COMMENT '任务运行日期，格式 yyyy-MM-dd');

-- ===== yz_event3_t1_daily_cnt =====
CREATE TABLE ec_risk_model_dev.yz_event3_t1_daily_cnt (
    loan_account_id STRING COMMENT '贷款账户ID',
    event_code      STRING COMMENT '事件编码',
    daily_cnt       INT    COMMENT '当日事件次数',
    daily_dur_sum   DOUBLE COMMENT '当日事件时长总和（秒）',
    daily_dur_max   DOUBLE COMMENT '当日事件时长最大值（秒）'
) COMMENT '埋点T+1特征 每日事件计数中间层'
PARTITIONED BY (event_date STRING COMMENT '事件日期，格式 yyyy-MM-dd');
