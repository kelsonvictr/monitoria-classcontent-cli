"""Sync — sends code snapshots to ClassContent API."""

from __future__ import annotations

import gzip
import hashlib
import json
import time
from pathlib import Path

import httpx

from monitoria.config import MonitoriaConfig


class SyncError(Exception):
    """Custom error for sync failures with status info."""

    def __init__(self, message: str, code: str | None = None, status: int = 0):
        super().__init__(message)
        self.code = code
        self.status = status


def compute_content_hash(files: list[dict]) -> str:
    """Compute a SHA256 hash of all file contents to detect changes."""
    h = hashlib.sha256()
    for f in sorted(files, key=lambda x: x.get("path", "")):
        h.update(f.get("path", "").encode())
        h.update(f.get("content", "").encode())
    return h.hexdigest()[:16]


def fetch_active_session(config: MonitoriaConfig) -> dict | None:
    """Check if there's an active session for the configured class.

    Returns session dict or None.
    Raises SyncError on non-404 errors.
    """
    if not config.token or not config.class_id:
        return None

    try:
        response = httpx.get(
            f"{config.api_url}/monitor/session/active",
            params={"classId": config.class_id},
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=15.0,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            return None

        if response.status_code == 401:
            raise SyncError("Token expirado — faça login novamente", code="AUTH_EXPIRED", status=401)

        return None

    except httpx.HTTPError:
        return None


def sync_snapshot(
    config: MonitoriaConfig,
    files: list[dict],
    project_path: Path,
    *,
    content_hash: str = "",
    last_hash: str = "",
) -> dict | None:
    """Send a code snapshot to the ClassContent API.

    Returns API response dict if sync was successful, None otherwise.
    Raises SyncError for session status issues (paused/ended).
    """
    if not config.token or not config.class_id:
        return None

    payload: dict = {
        "classId": config.class_id,
        "files": files,
        "projectType": _detect_project_type(project_path),
        "totalFiles": len(files),
        "totalLines": sum(f["content"].count("\n") + 1 for f in files),
        "contentHash": content_hash,
        "lastHash": last_hash,
    }

    # Compress payload
    json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    compressed = gzip.compress(json_bytes)

    try:
        response = httpx.post(
            f"{config.api_url}/monitor/sync",
            content=compressed,
            headers={
                "Authorization": f"Bearer {config.token}",
                "Content-Type": "application/json",
                "Content-Encoding": "gzip",
            },
            timeout=30.0,
        )

        if response.status_code in (200, 202):
            config.last_sync_at = time.strftime("%Y-%m-%d %H:%M:%S")
            config.save()
            return response.json()

        if response.status_code == 401:
            raise SyncError("Token expirado — faça login novamente", code="AUTH_EXPIRED", status=401)

        if response.status_code == 404:
            data = response.json() if response.content else {}
            code = data.get("code", "")
            if code == "NO_SESSION":
                raise SyncError("Nenhuma aula em andamento", code="NO_SESSION", status=404)
            return None

        if response.status_code == 423:
            raise SyncError("Aula pausada pelo professor", code="SESSION_PAUSED", status=423)

        if response.status_code == 410:
            raise SyncError("Aula encerrada", code="SESSION_ENDED", status=410)

        return None

    except httpx.HTTPError:
        return None


def _detect_project_type(project_path: Path) -> str:
    """Detect project type from common config files."""
    indicators = {
        "pom.xml": "java-maven",
        "build.gradle": "java-gradle",
        "build.gradle.kts": "kotlin-gradle",
        "package.json": "node",
        "requirements.txt": "python",
        "pyproject.toml": "python",
        "Cargo.toml": "rust",
        "go.mod": "go",
        "CMakeLists.txt": "cpp-cmake",
        "Makefile": "make",
    }

    for filename, project_type in indicators.items():
        if (project_path / filename).exists():
            return project_type

    return "unknown"
