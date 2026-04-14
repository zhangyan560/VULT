"""
埋点 T+1 特征离线回溯
通过 impala.dbapi 连接 HiveServer2，顺序执行 5 步 CTAS：
  feat_a → feat_b → feat_c → feat_d → features

每步生成并执行 CREATE TABLE {output_prefix}_{feat} AS SELECT ...
执行前自动 DROP TABLE IF EXISTS，支持幂等重跑。
"""

import time
from impala.dbapi import connect

# ══════════════════ 配置区 ═══════════════════════════════════════════════════

HIVE_HOST = '172.29.245.53'
HIVE_PORT = 10000
HIVE_USER = 'yanzhang1'
HIVE_PASS = 'Rr--112211'

TRACE_TABLE   = 'risk_data.yz_event3_firstloan_reloan_firstbase_lite'
OUTPUT_PREFIX = 'risk_data.yz_event3_backfill'   # 输出表前缀
MIN_ANCHOR    = '2025-01-01'                       # 最早锚点，用于缩小 event_log 扫描范围
MAX_ANCHOR    = '2026-02-01'                       # 最晚锚点（不含）

# 要运行的步骤，注释掉已完成的可跳过
# daily_cnt 必须先于 a/b 执行
TASKS = ['daily_cnt', 'a', 'b', 'c', 'd', 'merge']

# ══════════════════ Hive 连接 ════════════════════════════════════════════════

def get_conn():
    return connect(
        host=HIVE_HOST, port=HIVE_PORT,
        user=HIVE_USER, password=HIVE_PASS,
        auth_mechanism='PLAIN',
    )

def run_hive(sql: str, label: str = ''):
    """执行 DDL/DML（CTAS、DROP TABLE），不返回行数据。"""
    conn = get_conn()
    cur  = conn.cursor()
    t0   = time.time()
    print(f'[{time.strftime("%H:%M:%S")}] {label or "执行 SQL"} ...')
    cur.execute(sql)
    conn.close()
    print(f'  → 完成，耗时 {time.time()-t0:.1f}s')

def drop_and_ctas(table: str, sql: str, label: str = ''):
    """DROP TABLE IF EXISTS 再 CTAS，幂等可重跑。"""
    run_hive(f'DROP TABLE IF EXISTS {table}', f'DROP {table}')
    run_hive(sql, label or f'CTAS {table}')

# ══════════════════ 主流程 ═══════════════════════════════════════════════════

# 导入 SQL 生成器（与本文件同目录）
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from sql_daily_cnt import sql_daily_cnt
from sql_feat_a    import sql_feat_a
from sql_feat_b    import sql_feat_b
from sql_feat_c    import sql_feat_c
from sql_feat_d    import sql_feat_d
from sql_merge     import sql_merge

kw = dict(
    trace_table   = TRACE_TABLE,
    output_prefix = OUTPUT_PREFIX,
    min_anchor    = MIN_ANCHOR,
    max_anchor    = MAX_ANCHOR,
)
p = OUTPUT_PREFIX

if 'daily_cnt' in TASKS:
    drop_and_ctas(f'{p}_daily_cnt', sql_daily_cnt(**kw),
                  'daily_cnt（从 event_log 聚合，人群限定 trace 表）')

if 'a' in TASKS:
    drop_and_ctas(f'{p}_feat_a', sql_feat_a(**kw), 'feat_a（Dim1-4 + Dim5-simple）')

if 'b' in TASKS:
    drop_and_ctas(f'{p}_feat_b', sql_feat_b(**kw), 'feat_b（Dim5-complex）')

if 'c' in TASKS:
    drop_and_ctas(f'{p}_feat_c', sql_feat_c(**kw), 'feat_c（Dim6 时间间隔）')

if 'd' in TASKS:
    drop_and_ctas(f'{p}_feat_d', sql_feat_d(**kw), 'feat_d（Dim7 A→B 序列）')

if 'merge' in TASKS:
    drop_and_ctas(f'{p}_features', sql_merge(p), 'features（最终合并宽表）')

print('\n[backfill] 全部完成')
