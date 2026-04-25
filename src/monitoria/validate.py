"""Pre-watch validation — hardcoded blocklist + Haiku-based directory check.

Two layers:
1. Blocklist hard-coded (HOME, ~/Desktop, ~/Library, /, etc) — catastrophic paths
   that should NEVER be watched, regardless of session context. Protects against
   privacy leaks and runaway FinOps.
2. Server-side Haiku check — compares the file tree with the active session's
   context (objective, technologies). Catches "wrong project" mistakes.
"""

from __future__ import annotations

from pathlib import Path

import httpx

from monitoria.config import MonitoriaConfig


class WatchDirBlocked(Exception):
    """Raised when the path matches the hard-coded blocklist."""


def _build_blocklist() -> set[Path]:
    home = Path.home()
    candidates = [
        home,
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        home / "Library",
        home / "Music",
        home / "Movies",
        home / "Pictures",
        home / "Public",
        home / ".ssh",
        home / ".aws",
        home / ".config",
        home / ".cache",
        home / ".local",
        home / ".monitoria",
        Path("/"),
        Path("/Users"),
        Path("/home"),
        Path("/etc"),
        Path("/var"),
        Path("/tmp"),
        Path("/usr"),
        Path("/private"),
        Path("/Applications"),
    ]
    out: set[Path] = set()
    for p in candidates:
        try:
            out.add(p.resolve())
        except OSError:
            pass
    return out


def check_blocklist(project_path: Path) -> None:
    """Raise WatchDirBlocked if the path is a system/user directory."""
    resolved = project_path.resolve()
    if resolved in _build_blocklist():
        raise WatchDirBlocked(
            f"'{resolved}' é uma pasta do sistema ou pasta pessoal completa. "
            "MonitorIA não permite watch aí — risco de privacidade e custos. "
            "Aponte para uma subpasta com seu projeto (ex: ~/IdeaProjects/aula-X)."
        )


def collect_file_tree(
    project_path: Path,
    config: MonitoriaConfig,
) -> tuple[list[dict], int]:
    """Lightweight tree (paths + sizes only, no content) for validation.

    Returns (entries, total_size_bytes).
    """
    ext_set = set(config.extensions)
    ignore_set = set(config.ignore_dirs)
    entries: list[dict] = []
    total_bytes = 0

    for p in project_path.rglob("*"):
        if p.is_dir():
            continue
        if any(part in ignore_set for part in p.parts):
            continue
        if p.suffix not in ext_set:
            continue
        try:
            sz = p.stat().st_size
        except OSError:
            continue
        if sz > config.max_file_size_kb * 1024:
            continue
        entries.append({
            "path": str(p.relative_to(project_path)),
            "sizeBytes": sz,
        })
        total_bytes += sz

    return entries, total_bytes


def validate_watch_dir(
    config: MonitoriaConfig,
    project_path: Path,
) -> dict | None:
    """Ask backend to validate the directory using Haiku.

    Returns dict with: decision (OK/SUSPEITO/RECUSADO), reason, checked, sessionTitle.
    Returns None on network/auth failure (caller decides what to do — usually proceed
    with a warning, since blocking on transient backend errors would be hostile).
    """
    if not config.token or not config.class_id:
        return None

    entries, total_size = collect_file_tree(project_path, config)
    total_files = len(entries)

    payload = {
        "classId": config.class_id,
        "tree": entries[:80],
        "totalFiles": total_files,
        "totalSizeBytes": total_size,
        "projectBasename": project_path.name,
    }

    try:
        response = httpx.post(
            f"{config.api_url}/monitor/validate-watch-dir",
            json=payload,
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=20.0,
        )
        if response.status_code == 200:
            return response.json()
        if response.status_code == 401:
            return {
                "decision": "OK",
                "reason": "Token expirado — pulando validação.",
                "checked": False,
            }
        return None
    except httpx.HTTPError:
        return None
