"""
埋点 T+1 定时任务 — 执行调度器

用法：
    # T+1 单日执行（默认昨日）
    python3 run_t1_daily.py

    # 指定日期
    python3 run_t1_daily.py --dt 2026-04-08

    # 回溯多日
    python3 run_t1_daily.py --start 2026-01-01 --end 2026-04-08

    # 只跑某些 Job
    python3 run_t1_daily.py --dt 2026-04-08 --job A,B

    # dry-run 只生成 SQL 不执行
    python3 run_t1_daily.py --dt 2026-04-08 --dry-run
"""

import argparse
import logging
import os
import sys
import time
import gc
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager

from impala.dbapi import connect as impala_connect

from gen_hive_sql import generate_sql, ALL_JOBS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("t1_daily")

HIVE_HOST = "10.126.32.248"
HIVE_PORT = 10000
HIVE_DB = "default"
HIVE_AUTH = "LDAP"
HIVE_USER = "yanzhang1"
HIVE_PASSWORD = os.environ.get("HIVE_PASSWORD", "yz@dp24")


@contextmanager
def hive_cursor(host=HIVE_HOST, port=HIVE_PORT, database=HIVE_DB):
    """获取 Hive cursor 的上下文管理器"""
    conn = impala_connect(
        host=host, port=port, database=database,
        auth_mechanism=HIVE_AUTH, user=HIVE_USER, password=HIVE_PASSWORD,
    )
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()


def execute_sql(cur, sql: str, job_name: str = ""):
    """执行一段可能包含多条 SQL 的脚本"""
    stmts = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    for i, stmt in enumerate(stmts, 1):
        t0 = time.time()
        preview = stmt[:120].replace("\n", " ")
        log.info(f"[{job_name}] 执行 SQL {i}/{len(stmts)}: {preview}...")
        try:
            cur.execute(stmt)
            elapsed = time.time() - t0
            log.info(f"[{job_name}] SQL {i}/{len(stmts)} 完成 ({elapsed:.1f}s)")
        except Exception as e:
            log.error(f"[{job_name}] SQL {i}/{len(stmts)} 失败: {e}")
            raise


def run_job(job: str, dt: str, mode: str, dry_run: bool = False, sql_dir: str = "sql"):
    """执行单个 Job"""
    t0 = time.time()
    log.info(f"=== Job {job} 开始 (dt={dt}, mode={mode}) ===")

    sql = generate_sql(mode, job, dt)

    os.makedirs(sql_dir, exist_ok=True)
    sql_file = os.path.join(sql_dir, f"{job}_{dt}.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql)

    if dry_run:
        log.info(f"[{job}] dry-run: SQL 已写入 {sql_file}")
        return job, 0

    with hive_cursor() as cur:
        execute_sql(cur, sql, job)

    elapsed = time.time() - t0
    log.info(f"=== Job {job} 完成 ({elapsed:.1f}s) ===")
    return job, elapsed


def run_pipeline(dt: str, jobs: list, mode: str = "t1",
                 dry_run: bool = False, sql_dir: str = "sql",
                 max_workers: int = 2):
    """T+1 完整 pipeline"""
    t_total = time.time()
    timings = {}

    sequential_jobs = [j for j in ["ddl", "base", "daily_cnt"] if j in jobs]
    for job in sequential_jobs:
        _, elapsed = run_job(job, dt, mode, dry_run, sql_dir)
        timings[job] = elapsed

    parallel_jobs = [j for j in ["A", "B", "C", "D"] if j in jobs]
    if parallel_jobs:
        log.info(f"并行执行 Job: {parallel_jobs} (workers={max_workers})")
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(run_job, job, dt, mode, dry_run, sql_dir): job
                for job in parallel_jobs
            }
            for future in as_completed(futures):
                job_name = futures[future]
                try:
                    _, elapsed = future.result()
                    timings[job_name] = elapsed
                except Exception as e:
                    log.error(f"Job {job_name} 失败: {e}")
                    raise

    if "merge" in jobs:
        _, elapsed = run_job("merge", dt, mode, dry_run, sql_dir)
        timings["merge"] = elapsed

    total_elapsed = time.time() - t_total
    log.info(f"\n{'='*50}")
    log.info(f"Pipeline 完成 — dt={dt}")
    log.info(f"{'='*50}")
    for j, t in timings.items():
        log.info(f"  {j:12s} : {t:>8.1f}s")
    log.info(f"  {'─'*25}")
    log.info(f"  {'TOTAL':12s} : {total_elapsed:>8.1f}s")
    log.info(f"{'='*50}\n")

    gc.collect()
    return timings


def main():
    parser = argparse.ArgumentParser(description="埋点 T+1 定时任务调度器")
    parser.add_argument("--dt", help="执行日期 YYYY-MM-DD（默认昨日）")
    parser.add_argument("--start", help="回溯起始日期")
    parser.add_argument("--end", help="回溯结束日期")
    parser.add_argument("--job", default="all", help="Job 名称，逗号分隔或 all")
    parser.add_argument("--mode", choices=["t1", "hist"], default="t1")
    parser.add_argument("--dry-run", action="store_true", help="只生成 SQL 不执行")
    parser.add_argument("--sql-dir", default="sql", help="SQL 输出目录")
    parser.add_argument("--workers", type=int, default=2, help="并行 Job 数量")
    args = parser.parse_args()

    jobs = ALL_JOBS if args.job == "all" else [j.strip() for j in args.job.split(",")]

    if args.start and args.end:
        start = datetime.strptime(args.start, "%Y-%m-%d")
        end = datetime.strptime(args.end, "%Y-%m-%d")
        current = start
        while current <= end:
            dt_str = current.strftime("%Y-%m-%d")
            run_pipeline(dt_str, jobs, args.mode, args.dry_run, args.sql_dir, args.workers)
            current += timedelta(days=1)
    else:
        dt = args.dt or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        run_pipeline(dt, jobs, args.mode, args.dry_run, args.sql_dir, args.workers)


if __name__ == "__main__":
    main()
