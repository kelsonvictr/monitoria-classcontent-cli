"""TUI — Rich Terminal UI for MonitorIA.

Displays a live dashboard with file status, AI analysis feedback, and sync info.
"""

from __future__ import annotations

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


SEVERITY_STYLES = {
    "error": ("❌", "bold red"),
    "warning": ("⚠️ ", "yellow"),
    "info": ("💡", "dim cyan"),
}


def build_header(
    version: str,
    class_id: str | None,
    class_name: str | None,
    project_path: str,
    mode: str,
    session_title: str | None = None,
    session_status: str | None = None,
) -> Panel:
    """Build the header panel."""
    mode_label = "[yellow]OFFLINE[/yellow]" if mode == "offline" else "[green]ONLINE[/green]"
    text = Text.assemble(
        ("🤖 MonitorIA", "bold magenta"),
        (f" v{version}", "dim"),
        ("  │  ", "dim"),
        ("Turma: ", "dim"),
        (class_name or class_id or "N/A", "cyan"),
        ("  │  ", "dim"),
        ("Modo: ", "dim"),
    )
    text.append_text(Text.from_markup(mode_label))

    if session_title:
        status_map = {
            "active": "[green]● Ao vivo[/green]",
            "paused": "[yellow]⏸ Pausada[/yellow]",
            "ended": "[dim]■ Encerrada[/dim]",
        }
        status_label = status_map.get(session_status or "", "[dim]?[/dim]")
        text.append("  │  ", style="dim")
        text.append(f"Aula: {session_title} ", style="white")
        text.append_text(Text.from_markup(status_label))

    return Panel(text, style="bright_magenta", height=3)


def build_files_panel(tracked_files: list[dict], dirty_count: int) -> Panel:
    """Build panel showing tracked files."""
    table = Table(show_header=True, header_style="bold", expand=True, box=None, padding=(0, 1))
    table.add_column("Arquivo", style="cyan", ratio=3)
    table.add_column("Linguagem", style="dim", ratio=1)
    table.add_column("Linhas", justify="right", style="dim", ratio=1)
    table.add_column("Status", justify="center", ratio=1)

    # Show last 15 files max
    display_files = tracked_files[-15:] if len(tracked_files) > 15 else tracked_files
    for f in display_files:
        lines_count = f.get("content", "").count("\n") + 1
        table.add_row(
            f["path"],
            f.get("language", "?"),
            str(lines_count),
            "✓",
        )

    if len(tracked_files) > 15:
        table.add_row(f"... +{len(tracked_files) - 15} arquivos", "", "", "", style="dim")

    title = f"📁 Arquivos Monitorados ({len(tracked_files)})"
    if dirty_count > 0:
        title += f"  [yellow]● {dirty_count} modificado(s)[/yellow]"

    return Panel(table, title=title, border_style="blue", height=20)


def build_score_panel(
    ai_score: int | None,
    ai_summary: str | None,
    ai_positives: list[str] | None,
) -> Panel:
    """Build the score/status panel with AI data."""
    if ai_score is None:
        return Panel(
            Text("Aguardando análise da IA...", style="dim"),
            title="🤖 Score IA",
            border_style="dim",
            height=10,
        )

    score = ai_score
    if score >= 80:
        score_style = "bold green"
        emoji = "🟢"
    elif score >= 50:
        score_style = "bold yellow"
        emoji = "🟡"
    else:
        score_style = "bold red"
        emoji = "🔴"

    score_text = Text()
    score_text.append(f"\n  {emoji} ", style="")
    score_text.append(f"{score}", style=score_style)
    score_text.append("/100\n\n", style="dim")

    if ai_summary:
        # Truncate summary if too long
        summary = ai_summary[:80] + "..." if len(ai_summary) > 80 else ai_summary
        score_text.append(f"  {summary}\n\n", style="white")

    if ai_positives:
        for pos in ai_positives[:3]:
            score_text.append(f"  ✅ {pos}\n", style="green")

    return Panel(score_text, title="🤖 Score IA", border_style="magenta", height=10)


def build_issues_panel(ai_issues: list[dict] | None) -> Panel:
    """Build the issues list panel with AI-detected issues."""
    if ai_issues is None or len(ai_issues) == 0:
        msg = "✅ Nenhum problema detectado!" if ai_issues is not None else "Aguardando análise..."
        return Panel(
            Text(f"\n  {msg}", style="green" if ai_issues is not None else "dim"),
            title="🔍 Problemas (IA)",
            border_style="dim" if ai_issues is None else "green",
        )

    table = Table(show_header=True, header_style="bold", expand=True, box=None, padding=(0, 1))
    table.add_column("", width=3)  # severity icon
    table.add_column("Arquivo", style="cyan", ratio=2, no_wrap=True)
    table.add_column("Ln", justify="right", style="dim", width=4)
    table.add_column("Problema", ratio=5)

    # Sort: errors first, then warnings, then info
    severity_order = {"error": 0, "warning": 1, "info": 2}
    sorted_issues = sorted(ai_issues, key=lambda i: severity_order.get(i.get("severity", "info"), 9))

    # Show max 20 issues
    shown = sorted_issues[:20]
    for issue in shown:
        sev = issue.get("severity", "info")
        icon, style = SEVERITY_STYLES.get(sev, ("?", ""))
        file_name = issue.get("file", "?")
        line_num = str(issue.get("line", "")) if issue.get("line") else ""
        message = issue.get("message", "")
        table.add_row(
            icon,
            _truncate(file_name, 30),
            line_num,
            Text(message, style=style),
        )

    if len(sorted_issues) > 20:
        table.add_row("", f"... +{len(sorted_issues) - 20} problemas", "", "", style="dim")

    error_count = sum(1 for i in ai_issues if i.get("severity") == "error")
    title = f"🔍 Problemas IA ({len(ai_issues)})"
    return Panel(table, title=title, border_style="red" if error_count else "yellow")


def build_log_panel(log_lines: list[str]) -> Panel:
    """Build the activity log panel."""
    text = Text()
    # Show last 5 log entries
    for line in log_lines[-5:]:
        text.append(f"  {line}\n", style="dim")

    if not log_lines:
        text.append("  Aguardando atividade...\n", style="dim")

    return Panel(text, title="📋 Log", border_style="dim", height=8)


def build_dashboard(
    version: str,
    class_id: str | None,
    class_name: str | None,
    project_path: str,
    mode: str,
    tracked_files: list[dict],
    dirty_count: int,
    ai_score: int | None,
    ai_summary: str | None,
    ai_issues: list[dict] | None,
    ai_positives: list[str] | None,
    session_title: str | None,
    session_status: str | None,
    log_lines: list[str],
) -> Layout:
    """Build the complete TUI dashboard layout."""
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=8),
    )

    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2),
    )

    layout["left"].split_column(
        Layout(name="files", ratio=2),
        Layout(name="score", ratio=1),
    )

    # Populate panels
    layout["header"].update(build_header(
        version, class_id, class_name, project_path, mode,
        session_title, session_status,
    ))
    layout["files"].update(build_files_panel(tracked_files, dirty_count))
    layout["score"].update(build_score_panel(ai_score, ai_summary, ai_positives))
    layout["right"].update(build_issues_panel(ai_issues))
    layout["footer"].update(build_log_panel(log_lines))

    return layout


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"
