
---wa宽表


drop table risk_data.wyj_wa_detail;
create table risk_data.wyj_wa_detail as
select a.created_date,n.user_id as user_idd,
count(distinct case when  a.delivery_status in (1,2) then msg_id end) as cnt_wa,
count(distinct case when  a.delivery_status in (2) then msg_id end) as cnt_read from
(select * from ec_dwd.dwd_ec_col_df_whatopia_chat_info
where dt=date_format(date_add(current_date(),-1),'yyyyMMdd')
and created_date >='2025-06-01'
and from_operator='T'
and biz_team not in ('印尼催收')) a
join (select * from ec_dim.dim_ec_df_user_info
where dt=date_format(date_sub(current_date(), 1), 'yyyyMMdd')
) n
on a.link_mobile_number=n.mobile_number
and n.register_ts<=a.created_ts

group by 1,2
;

----uplift样本宽表

drop table risk_data.wyj_model_uplift_base;
create table risk_data.wyj_model_uplift_base as 

select '结清客群实验' as exp_flag , a.*,case when b.user_idd is not null then 'Y' else 'N' end as wa_sent_flag,---当天是否触达
b.cnt_wa,----当天发了几次
case when b.cnt_read >0 then 'Y' else 'N' end as wa_read_flag----当天是否已读
 from (
select distinct  case when strategy_unique_id in ('714947550139076627') then '对照组-旧话术'
when strategy_unique_id = '714947550139076636' then '对照组-固定话术'
when strategy_unique_id = '714947550139076608' then '实验组-好话术' 
when strategy_unique_id = '714950387183079425' then '长期空白组' end as group_flag ,first_notif_create_date,user_id,
case when datediff(post_ops_first_payout_date,first_notif_create_date) between 0 and 7 then 'Y' else 'N' end as payout_flag
from dm_id.dm_id_ops_df_strategy_transform
where dt = '20251203'
and scene_id = 4923
and first_notif_create_date between '2025-09-17' and '2025-10-22'
and strategy_unique_id in ('714947550139076608','714947550139076627','714947550139076636','714950387183079425')
) a 
left join risk_data.wyj_wa_detail b 
on a.user_id = b.user_idd 
and a.first_notif_create_date = b.created_date

union all 
select '续借客群实验' as exp_flag ,  a.*,case when b.user_idd is not null then 'Y' else 'N' end as wa_sent_flag,---当天是否触达
b.cnt_wa,----当天发了几次
case when b.cnt_read >0 then 'Y' else 'N' end as wa_read_flag-----当天是否已读
 from (
select distinct  case when strategy_desc = 'PUSH+WA(utility手机号)' then '对照组-旧话术'
when strategy_desc = 'PUSH+WA(utility额度)' then '实验组-好话术' 
when strategy_desc = '泳道对照组' then '长期空白组' end as group_flag ,first_notif_create_date,user_id,
case when datediff(post_ops_first_payout_date,first_notif_create_date) between 0 and 7 then 'Y' else 'N' end as payout_flag 
from dm_id.dm_id_ops_df_strategy_transform
where dt = '20251203'
and scene_id = 4914 
and first_notif_create_date between '2025-11-11' and '2025-12-03'
and strategy_desc in ('PUSH+WA(utility额度)','PUSH+WA(utility手机号)','泳道对照组')
) a 
left join risk_data.wyj_wa_detail b 
on a.user_id = b.user_idd
and a.first_notif_create_date = b.created_date
;
----描述性统计

select exp_flag, group_flag ,count(distinct case when wa_sent_flag = 'Y' then user_id end),
count(distinct case when wa_sent_flag <> 'Y' then user_id end)
 from risk_data.wyj_model_uplift_base
 group by 1,2
 ;