#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from agent_provider import configure_model_provider, load_local_env


VAULT_ROOT = Path(__file__).resolve().parents[5]
WORK_LOG_ROOT = VAULT_ROOT / "work" / "日志"
DAILY_PROGRESS_DIR = WORK_LOG_ROOT / "每日进展"
WEEKLY_REPORT_DIR = WORK_LOG_ROOT / "周报"
DAILY_TEMPLATE_PATH = DAILY_PROGRESS_DIR / "_模板.md"
REFERENCE_WEEKLY_REPORT = WORK_LOG_ROOT / "2026-05-15周报.md"


@dataclass
class WeeklyReportContext:
    start_date: date
    end_date: date
    daily_progress_dir: Path
    output_dir: Path
    daily_template_path: Path
    reference_weekly_report_path: Path | None
    max_source_notes: int = 14


class WeeklyReportDraft(BaseModel):
    report_title: str = Field(description="Human-readable weekly report title in Chinese.")
    output_filename: str = Field(description="Target markdown filename, for example 2026-05-21_周报.md.")
    summary_markdown: str = Field(description="Full markdown content for the weekly report.")
    source_notes: list[str] = Field(description="Daily progress note paths used as source material.")


def detect_default_window(today: date) -> tuple[date, date]:
    start = today - timedelta(days=6)
    return start, today


def parse_note_date(path: Path) -> date | None:
    try:
        return datetime.strptime(path.name[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def collect_daily_progress_paths(ctx: WeeklyReportContext) -> list[Path]:
    candidates: list[Path] = []
    for path in sorted(ctx.daily_progress_dir.glob("*_工作进展.md")):
        note_date = parse_note_date(path)
        if note_date is None:
            continue
        if ctx.start_date <= note_date <= ctx.end_date:
            candidates.append(path)
    return candidates[: ctx.max_source_notes]


def serialize_file(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path.relative_to(VAULT_ROOT)),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "size_bytes": stat.st_size,
    }


def write_weekly_report(ctx: WeeklyReportContext, draft: WeeklyReportDraft) -> Path:
    ctx.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = ctx.output_dir / draft.output_filename
    output_path.write_text(draft.summary_markdown.strip() + "\n", encoding="utf-8")
    return output_path


async def build_weekly_report_agent() -> tuple[Any, WeeklyReportContext]:
    load_local_env()
    model = configure_model_provider()

    from agents import Agent, RunContextWrapper, function_tool

    today = date.today()
    start_date, end_date = detect_default_window(today)
    report_context = WeeklyReportContext(
        start_date=start_date,
        end_date=end_date,
        daily_progress_dir=DAILY_PROGRESS_DIR,
        output_dir=WEEKLY_REPORT_DIR,
        daily_template_path=DAILY_TEMPLATE_PATH,
        reference_weekly_report_path=REFERENCE_WEEKLY_REPORT if REFERENCE_WEEKLY_REPORT.exists() else None,
    )

    async def weekly_report_instructions(
        run_ctx: RunContextWrapper[WeeklyReportContext], agent: Agent[WeeklyReportContext]
    ) -> str:
        ctx = run_ctx.context
        return (
            "你是周报撰写专家。你的任务是基于日报素材输出一份中文 Markdown 周报。"
            " 只根据工具返回的内容写作，不要编造未出现的进展。"
            f" 本次周报覆盖时间范围是 {ctx.start_date.isoformat()} 到 {ctx.end_date.isoformat()}。"
            " 优先提炼项目背景、当前进展、关键结论、风险和下周 todo。"
            " 写作风格参考现有周报，结构清晰，适合直接存档。"
            " 输出必须符合结构化 schema。"
        )

    @function_tool
    def list_daily_progress_notes(run_ctx: RunContextWrapper[WeeklyReportContext]) -> str:
        """List daily progress notes in the current weekly window."""
        notes = [serialize_file(path) for path in collect_daily_progress_paths(run_ctx.context)]
        return json.dumps(
            {
                "start_date": run_ctx.context.start_date.isoformat(),
                "end_date": run_ctx.context.end_date.isoformat(),
                "notes": notes,
            },
            ensure_ascii=False,
            indent=2,
        )

    @function_tool
    def read_daily_progress_note(
        run_ctx: RunContextWrapper[WeeklyReportContext], relative_path: str
    ) -> str:
        """Read one daily progress note by its vault-relative path."""
        target = (VAULT_ROOT / relative_path).resolve()
        if not target.is_file():
            raise FileNotFoundError(f"Note not found: {relative_path}")
        return target.read_text(encoding="utf-8")

    @function_tool
    def read_daily_progress_template(run_ctx: RunContextWrapper[WeeklyReportContext]) -> str:
        """Read the daily progress template used as source structure."""
        return run_ctx.context.daily_template_path.read_text(encoding="utf-8")

    @function_tool
    def read_reference_weekly_report(run_ctx: RunContextWrapper[WeeklyReportContext]) -> str:
        """Read one existing weekly report as a style reference."""
        ref = run_ctx.context.reference_weekly_report_path
        if ref is None:
            return "No reference weekly report is available."
        return ref.read_text(encoding="utf-8")

    agent = Agent[WeeklyReportContext](
        name="周报撰写专家",
        handoff_description="Draft weekly work reports from daily progress notes.",
        instructions=weekly_report_instructions,
        model=model,
        tools=[
            list_daily_progress_notes,
            read_daily_progress_note,
            read_daily_progress_template,
            read_reference_weekly_report,
        ],
        output_type=WeeklyReportDraft,
    )
    return agent, report_context


async def run_weekly_report_agent() -> Path:
    from agents import Runner

    agent, report_context = await build_weekly_report_agent()
    result = await Runner.run(
        agent,
        (
            "请根据本周日报自动生成周报。先查看本周有哪些日报，再阅读必要的日报和模板。"
            " 输出完整周报草稿，并给出 source_notes。"
        ),
        context=report_context,
        max_turns=12,
    )

    draft = result.final_output
    if not isinstance(draft, WeeklyReportDraft):
        raise RuntimeError(f"Unexpected output type: {type(draft)!r}")

    output_path = write_weekly_report(report_context, draft)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate weekly reports from daily progress notes.")
    parser.parse_args()
    output_path = asyncio.run(run_weekly_report_agent())
    print(output_path)


if __name__ == "__main__":
    main()
