"""
feat_d 离线回溯 SQL 生成器（Dim7 A→B 序列转化）

每个 pair CTE JOIN trace，在 anchor_date 截止前计算 A→B 转化次数/比率/时长。
注意：trace 表无 user_id，event_log 仅按 loan_account_id 关联。
"""

from config import EVENT_ALIAS, PAIR_CONFIG, TABLE_EVENT_LOG, MAX_LOOKBACK_DAYS

def _pair_alias(ev_a, ev_b):
    return f"{EVENT_ALIAS[ev_a]}_to_{EVENT_ALIAS[ev_b]}"

def _event_in_clause(events):
    return "(" + ",".join(f"'{e}'" for e in events) + ")"

def sql_feat_d(trace_table: str, output_prefix: str, min_anchor: str, max_anchor: str) -> str:
    table_write = f"{output_prefix}_feat_d"

    pair_events = list(dict.fromkeys(
        [a for a, _, _ in PAIR_CONFIG] + [b for _, b, _ in PAIR_CONFIG]
    ))

    pair_ctes    = []
    pair_selects = []

    for idx, (ev_a, ev_b, win_h) in enumerate(PAIR_CONFIG):
        pname   = f"p{idx}"
        pa      = _pair_alias(ev_a, ev_b)
        win_sec = int(win_h * 3600)

        pair_ctes.append(f"""{pname} AS (
    SELECT
        t.trace_id,
        t.anchor_date,
        a.loan_account_id,
        a.created_date AS a_time,
        MIN(CASE
            WHEN b.event_code = '{ev_b}'
             AND b.created_date > a.created_date
             AND TO_DATE(b.created_date) < t.anchor_date
             AND (UNIX_TIMESTAMP(b.created_date) - UNIX_TIMESTAMP(a.created_date)) <= {win_sec}
            THEN b.created_date
        END) AS first_b_time
    FROM trace t
    JOIN evt_filtered a
        ON  t.loan_account_id = a.loan_account_id
        AND TO_DATE(a.created_date) >= DATE_SUB(t.anchor_date, {MAX_LOOKBACK_DAYS})
        AND TO_DATE(a.created_date) <  t.anchor_date
    LEFT JOIN evt_filtered b ON a.loan_account_id = b.loan_account_id
    WHERE a.event_code = '{ev_a}'
    GROUP BY t.trace_id, t.anchor_date, a.loan_account_id, a.created_date
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
        f"LEFT JOIN p{i} ON uid.trace_id = p{i}.trace_id AND uid.loan_account_id = p{i}.loan_account_id"
        for i in range(len(PAIR_CONFIG))
    )

    return f"""
CREATE TABLE {table_write} AS
WITH trace AS (
    SELECT trace_id, loan_account_id, TO_DATE(anchor_date) AS anchor_date
    FROM {trace_table}
),
evt_filtered AS (
    SELECT e.loan_account_id, e.event_code, e.created_date
    FROM {TABLE_EVENT_LOG} e
    INNER JOIN (SELECT DISTINCT loan_account_id FROM trace) ids
        ON e.loan_account_id = ids.loan_account_id
    WHERE e.dt >= REGEXP_REPLACE(CAST(DATE_SUB('{min_anchor}', {MAX_LOOKBACK_DAYS + 1}) AS STRING), '-', '')
      AND e.event_code IN {_event_in_clause(pair_events)}
      AND e.loan_account_id IS NOT NULL
),
uid AS (SELECT DISTINCT trace_id, anchor_date, loan_account_id FROM trace),
{",".join(pair_ctes)}
SELECT
    uid.loan_account_id
{"".join(pair_selects)}
    ,uid.trace_id
    ,uid.anchor_date
FROM uid
{left_joins}
GROUP BY uid.trace_id, uid.loan_account_id, uid.anchor_date
"""
