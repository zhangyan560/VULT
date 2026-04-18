drop table if exists tmp_export.tmp_star_exp_usr_stat_byday;
create table tmp_export.tmp_star_exp_usr_stat_byday as 
select 
    t1.exp_id,
    max(exp_name) exp_name,
    max(lane_name) lane_name,
    t1.group_desc,
    t1.group_type,
    t1.exp_pct,
    min(t1.exp_fst_date) exp_fst_date,
    max(t1.exp_lst_date) exp_lst_date,
    t1.user_id,
    t1.stat_date,
    date_add('2025-01-10',int(datediff(t1.stat_date,'2025-01-10')/7)*7) stat_week,--周五到周四
    concat(substr(t1.stat_date,1,7),'-01') stat_mon,--自然月
    max(bf_available) bf_available,
    max(bf_credit) bf_credit,
    max(bf_credit_range) bf_credit_range,
    max(bf_rate_tag) bf_rate_tag,
    max(bf_af_range) bf_af_range,
    sum(wa_cnt) wa_cnt,
    sum(wa_succ_cnt) wa_succ_cnt,
    sum(wa_read_cnt) wa_read_cnt,
    sum(wa_clk_cnt) wa_clk_cnt,
    sum(push_cnt) push_cnt,
    sum(push_succ_cnt) push_succ_cnt,
    -- sum(ivr_cnt) ivr_cnt,
    count(t3.user_id) app_days,
    count(t8.user_id) loan_clk_days,
    sum(nvl(t4.loan_ordr_cnt,0)+nvl(t5.loan_ordr_cnt,0)) loan_ordr_cnt,
    sum(nvl(t4.loan_ordr_credit,0)+nvl(t5.loan_ordr_credit,0)) loan_ordr_credit,
    sum(nvl(t4.loan_ordr_principal,0)+nvl(t5.loan_ordr_principal,0)) loan_ordr_principal,
    sum(nvl(t4.payout_ordr_cnt,0)+nvl(t5.payout_ordr_cnt,0)) payout_ordr_cnt,
    sum(nvl(t4.payout_ordr_credit,0)+nvl(t5.payout_ordr_credit,0)) payout_ordr_credit,
    sum(nvl(t4.payout_ordr_principal,0)+nvl(t5.payout_ordr_principal,0)) payout_ordr_principal,
    sum(total_cost) total_cost,
    sum(tool_mkt_cost) tool_mkt_cost,
    sum(mkt_sms_cost) mkt_sms_cost,
    sum(opt_wa_cost) opt_wa_cost,
    sum(total_tel_cost) total_tel_cost,
    sum(total_ivr_cost) total_ivr_cost
from 
(
--入组用户
    select 
        exp_id,
        exp_name,
        lane_name,
        user_id,
        group_desc,
        group_type,
        usr_fst_ts,
        usr_fst_date,
        exp_fst_date,
        exp_lst_date,
        exp_pct,
        bf_available/2200 bf_available,
        bf_credit/2200 bf_credit,
                bf_credit_range,
        bf_rate_tag,
        bf_af_range,
        date_add(val,pos) stat_date
    from tmp_export.tmp_star_exp_usr
    LATERAL VIEW POSEXPLODE
                    ( SPLIT( TRIM( REPEAT( CONCAT(usr_fst_date, ' '), DATEDIFF(date_add(exp_lst_date, 1), usr_fst_date)) ), ' ' )
                    ) nn AS pos, val
)t1 
left join 
(
--回端
    -- select
    --     created_date stat_date,
    --     user_id
    -- from ec_dwd.dwd_ec_log_di_sa_app_events
    -- where dt>='20250801'
    -- and user_id is not null
    -- and event_code RLIKE '^(login_|auth_|loan_|post_|general_|other_|loanMarket_|middleincome_|\\$AppEnd|\\$AppStart)'
    -- group by 
    --     created_date,
    --     user_id
    select 
        active_date stat_date,
        user_id,
        max(last_active_ts) last_active_ts
    from ec_dwt.dwt_ec_ops_di_user_active_detail
    where dt>='20260101'
    and  platform_name = 'easycash_app'
    and user_id is not null 
    group by active_date,user_id
)t3
on t1.stat_date=t3.stat_date
and t1.user_id=t3.user_id
and t3.last_active_ts>t1.usr_fst_ts
left join 
(
--首日下单、放款
    select 
        exp_id,
        user_id,
        usr_fst_date,
        loan_ordr_cnt,
        loan_ordr_credit,
        loan_ordr_principal,
        payout_ordr_cnt,
        payout_ordr_credit,
        payout_ordr_principal
    from tmp_export.tmp_star_exp_usr_fst_stat
)t4
on t1.exp_id=t4.exp_id
and t1.user_id=t4.user_id
and t1.stat_date=t4.usr_fst_date
left join 
(
--非首日下单\放款
  select 
      to_date(order_created_time) stat_date,
      user_id,
      sum(1) loan_ordr_cnt,
      sum(order_credit)/2200 loan_ordr_credit,
      sum(order_principal)/2200 loan_ordr_principal,
      sum(if(order_payout_time>='2026-01-01',1,0)) payout_ordr_cnt,
      sum(if(order_payout_time>='2026-01-01',order_credit,0))/2200 payout_ordr_credit,
      sum(if(order_payout_time>='2026-01-01',order_principal,0))/2200 payout_ordr_principal
  from dm_id.dm_id_overview_df_business_process_detail
  where dt=date_format(date_add(current_date(),-1),'yyyyMMdd')
  and user_id is not null
  and order_created_time>='2026-01-01'
  group by 
      to_date(order_created_time),
      user_id
)t5
on t1.stat_date=t5.stat_date
and t1.user_id=t5.user_id
and t5.stat_date>t1.usr_fst_date
left join 
(
--成本
    select 
        stat_date,
        user_id,
        sum(mkt_sms_cost+opt_wa_cost+total_tel_cost+total_ivr_cost) tool_mkt_cost,
        sum(mkt_sms_cost+opt_wa_cost+total_tel_cost+total_ivr_cost+total_cpn_cost) total_cost,
        sum(mkt_sms_cost) mkt_sms_cost,
        sum(opt_wa_cost) opt_wa_cost,
        sum(total_tel_cost) total_tel_cost,
        sum(total_ivr_cost) total_ivr_cost,
        sum(total_cpn_cost) total_cpn_cost
    from tmp_export.mkt_mthd_cost_user
    where stat_date>='2026-01-01'
    group by 
        stat_date,
        user_id
)t7
on t1.stat_date=t7.stat_date
and t1.user_id=t7.user_id
left join 
(
--下单页点击
    SELECT 
        created_date stat_date,
        user_id,
        max(created_ts) last_active_ts
    FROM ec_dwd.dwd_ec_log_di_sa_app_events
    WHERE dt>='20260101'
    AND event_code rlike 'loan_b1_'
    AND event_code rlike 'click'
    AND event_code NOT IN ('loan_b1_d709_click', 'loan_b1_c702_d706_click', 'loan_b1_c2_d4_click', 'loan_b1_c746_d748_click') 
    AND (get_json_object(content, '$.properties.amount_modification_method') is null or get_json_object(content, '$.properties.amount_modification_method') <> 'AMOUNT_NON_USER_INPUT')
    AND platform_name = 'easycash_app' -- 限制app访问 
    group by 
        created_date,
        user_id
)t8
on t1.stat_date=t8.stat_date
and t1.user_id=t8.user_id
and t8.last_active_ts>t1.usr_fst_ts
left join 
(
--wa过程指标
    select 
        stat_date,
        user_id,
        sum(1) wa_cnt,
        SUM(if(delivery_status > 0,1,0)) AS wa_succ_cnt,
        SUM(if(delivery_status = 2,1,0)) AS wa_read_cnt,
        SUM(if(wa_clk_date>=stat_date,1,0)) AS wa_clk_cnt
    from tmp_export.tmp_star_wa_usr_msg
    where stat_date>='2026-01-01'
    group by stat_date,user_id
)t9
on t1.stat_date=t9.stat_date
and t1.user_id=t9.user_id
left join 
(
--push过程指标
    select 
        push_date stat_date,
        user_id,
                count(1) push_cnt,
                sum(is_succ) push_succ_cnt
    from tmp_export.tmp_star_push_usr_msg
    where push_date>='2026-01-01'
    group by push_date,user_id
)t10
on t1.stat_date=t10.stat_date
and t1.user_id=t10.user_id
-- left join 
-- (
--     select 
--         touch_created_date stat_date,
--         touch_user_id user_id,
--                 count(1) ivr_cnt
--     from tmp_export.touch_list_new0807
--     where touch_created_date>='2025-11-19'
--     and touch_tool in ('smartivr','ivr')
--     group by touch_created_date,user_id
-- )t8
-- on t1.stat_date=t8.stat_date
-- and t1.user_id=t8.user_id

-- left join 
-- (
--     select 
--         chatbot_date,
--         user_id,
--         chat_rst
--     from tmp_export.tmp_star_chatbot_usr
-- )t9
-- on t1.stat_date=t9.chatbot_date
-- and t1.user_id=t9.user_id
group by 
    t1.exp_id,
    t1.group_desc,
    t1.group_type,
    t1.exp_pct,
    t1.user_id,
    t1.stat_date
;