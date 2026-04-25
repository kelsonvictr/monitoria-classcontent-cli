"""File watcher — observes project directory and triggers sync + AI analysis."""

from __future__ import annotations

import time
import signal
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.live import Live
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
from watchdog.observers import Observer

from monitoria.config import MonitoriaConfig
from monitoria.tui import build_dashboard


class ProjectEventHandler(FileSystemEventHandler):
    """Tracks file changes and marks dirty files for next sync."""

    def __init__(self, config: MonitoriaConfig):
        self.config = config
        self.dirty_files: set[str] = set()
        self._ext_set = set(config.extensions)
        self._ignore_set = set(config.ignore_dirs)

    def _should_track(self, path: str) -> bool:
        """Check if file should be tracked based on extension and ignore rules."""
        p = Path(path)

        # Check ignored directories
        for part in p.parts:
            if part in self._ignore_set:
                return False

        # Check extension
        if p.suffix not in self._ext_set:
            return False

        # Check file size
        try:
            if p.stat().st_size > self.config.max_file_size_kb * 1024:
                return False
        except OSError:
            return False

        return True

    def on_modified(self, event: FileModifiedEvent):
        if not event.is_directory and self._should_track(event.src_path):
            self.dirty_files.add(event.src_path)

    def on_created(self, event: FileCreatedEvent):
        if not event.is_directory and self._should_track(event.src_path):
            self.dirty_files.add(event.src_path)

    def on_deleted(self, event: FileDeletedEvent):
        if not event.is_directory:
            self.dirty_files.discard(event.src_path)

    def flush_dirty(self) -> set[str]:
        """Return and clear the set of dirty file paths."""
        files = self.dirty_files.copy()
        self.dirty_files.clear()
        return files


def collect_all_files(project_path: Path, config: MonitoriaConfig) -> list[dict]:
    """Collect all tracked files for initial snapshot."""
    ext_set = set(config.extensions)
    ignore_set = set(config.ignore_dirs)
    files = []

    for p in project_path.rglob("*"):
        if p.is_dir():
            continue

        # Skip ignored dirs
        skip = False
        for part in p.parts:
            if part in ignore_set:
                skip = True
                break
        if skip:
            continue

        if p.suffix not in ext_set:
            continue

        try:
            if p.stat().st_size > config.max_file_size_kb * 1024:
                continue
        except OSError:
            continue

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            files.append({
                "path": str(p.relative_to(project_path)),
                "content": content,
                "language": _detect_language(p.suffix),
                "lastModified": int(p.stat().st_mtime * 1000),
            })
        except Exception:
            continue

    return files


def _detect_language(ext: str) -> str:
    """Map file extension to language identifier."""
    lang_map = {
        ".java": "java", ".py": "python",
        ".ts": "typescript", ".tsx": "typescript",
        ".js": "javascript", ".jsx": "javascript",
        ".html": "html", ".css": "css",
        ".xml": "xml", ".yml": "yaml", ".yaml": "yaml",
        ".json": "json", ".sql": "sql",
        ".kt": "kotlin", ".scala": "scala",
        ".c": "c", ".cpp": "cpp", ".h": "c",
    }
    return lang_map.get(ext, "text")


def _read_file_dict(file_path: Path, project_path: Path) -> dict | None:
    """Read a file into a file dict for analysis."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return {
            "path": str(file_path.relative_to(project_path)),
            "content": content,
            "language": _detect_language(file_path.suffix),
            "lastModified": int(file_path.stat().st_mtime * 1000),
        }
    except Exception:
        return None


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def start_watching(
    path: str,
    config: MonitoriaConfig,
    debounce: int,
    console: Console,
    *,
    offline: bool = False,
):
    """Start file watcher with live TUI dashboard.

    Online mode (default): syncs code to API, AI analyzes on server side.
    Offline mode: only tracks files locally (no API calls, no AI analysis).
    """
    from monitoria import __version__
    from monitoria.sync import (
        SyncError,
        compute_content_hash,
        fetch_active_session,
        sync_snapshot,
    )

    project_path = Path(path).resolve()
    config.merge_project_config(project_path)

    mode = "offline" if offline else "online"
    log_lines: list[str] = []

    # AI analysis state (from server responses)
    ai_score: int | None = None
    ai_summary: str | None = None
    ai_issues: list[dict] = []
    ai_positives: list[str] = []
    session_title: str | None = None
    session_status: str | None = None

    # Teacher mode state — when user is a teacher of the class, syncs are
    # published as the live reference code (not analyzed by Haiku).
    teacher_last_publish_at: float | None = None
    teacher_files_published: int = 0
    teacher_blob_bytes: int = 0

    # Content hash tracking
    last_content_hash: str = ""

    def log(msg: str):
        log_lines.append(f"[{_now()}] {msg}")
        if len(log_lines) > 50:
            log_lines.pop(0)

    def _update_ai_state(result: dict):
        """Update AI analysis state from API response."""
        nonlocal ai_score, ai_summary, ai_issues, ai_positives
        nonlocal teacher_last_publish_at, teacher_files_published, teacher_blob_bytes
        if result.get("mode") == "teacher":
            teacher_last_publish_at = time.time()
            teacher_files_published = int(result.get("filesPublished") or 0)
            teacher_blob_bytes = int(result.get("blobBytes") or 0)
            log(f"🎤 Gabarito publicado: {teacher_files_published} arquivos, {teacher_blob_bytes} bytes")
            return
        ai_data = result.get("aiAnalysis")
        if ai_data:
            ai_score = ai_data.get("score", 0)
            ai_summary = ai_data.get("summary", "")
            ai_issues = ai_data.get("issues", [])
            ai_positives = ai_data.get("positives", [])
            log(f"IA: score {ai_score}/100 — {len(ai_issues)} issues, {len(ai_positives)} positivos")
        elif not result.get("codeChanged", True):
            log("Código sem alterações — IA não reanalisou")

    # Set up file watcher
    handler = ProjectEventHandler(config)
    observer = Observer()
    observer.schedule(handler, str(project_path), recursive=True)

    # Graceful shutdown
    running = True

    def _shutdown(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # Collect initial files
    log("Coletando arquivos do projeto...")
    tracked_files = collect_all_files(project_path, config)
    log(f"Encontrados {len(tracked_files)} arquivos")

    # Check for active session (online mode)
    if not offline and config.token:
        log("Verificando sessão ativa...")
        try:
            session = fetch_active_session(config)
            if session:
                session_title = session.get("title", "")
                session_status = session.get("status", "")
                if session.get("isTeacher"):
                    mode = "teacher"
                    log(f"🎤 Você é professor desta turma — modo gabarito ao vivo ATIVADO")
                log(f"Sessão: {session_title} ({session_status})")
            else:
                log("⚠ Nenhuma aula em andamento — aguardando professor iniciar...")
        except SyncError as e:
            log(f"⚠ {e}")

    # Compute initial hash
    last_content_hash = compute_content_hash(tracked_files)

    # If online, do initial sync
    if not offline and config.token and tracked_files:
        log("Enviando snapshot para ClassContent...")
        try:
            result = sync_snapshot(
                config, tracked_files, project_path,
                content_hash=last_content_hash,
                last_hash="",
            )
            if result:
                log("Snapshot enviado ✓")
                _update_ai_state(result)
            else:
                log("Falha ao enviar snapshot ✗")
        except SyncError as e:
            log(f"⚠ {e}")

    # Start observer
    observer.start()
    log(f"Observando mudanças (sync a cada {debounce}s)... Ctrl+C para sair")

    last_sync_time = time.time()
    sync_count = 0

    try:
        with Live(
            build_dashboard(
                version=__version__,
                class_id=config.class_id,
                class_name=config.class_name,
                project_path=str(project_path),
                mode=mode,
                tracked_files=tracked_files,
                dirty_count=0,
                ai_score=ai_score,
                ai_summary=ai_summary,
                ai_issues=ai_issues,
                ai_positives=ai_positives,
                session_title=session_title,
                session_status=session_status,
                log_lines=log_lines,
                teacher_last_publish_at=teacher_last_publish_at,
                teacher_files_published=teacher_files_published,
                teacher_blob_bytes=teacher_blob_bytes,
            ),
            console=console,
            refresh_per_second=2,
            screen=True,
        ) as live:
            while running:
                time.sleep(0.5)

                dirty_count = len(handler.dirty_files)
                now = time.time()

                # Debounce: sync when enough time passed and files changed
                if dirty_count > 0 and (now - last_sync_time) >= debounce:
                    dirty_paths = handler.flush_dirty()
                    sync_count += 1
                    last_sync_time = now

                    # Update tracked files with new content
                    changed_files = []
                    for fp in dirty_paths:
                        p = Path(fp)
                        fd = _read_file_dict(p, project_path)
                        if fd:
                            changed_files.append(fd)
                            # Update or add in tracked_files
                            existing = next(
                                (f for f in tracked_files if f["path"] == fd["path"]),
                                None,
                            )
                            if existing:
                                existing.update(fd)
                            else:
                                tracked_files.append(fd)

                    if changed_files:
                        log(f"Sync #{sync_count}: {len(changed_files)} arquivo(s) modificado(s)")

                        # Compute new content hash
                        new_hash = compute_content_hash(tracked_files)

                        # If online, sync to API (AI analysis happens server-side)
                        if not offline and config.token:
                            try:
                                result = sync_snapshot(
                                    config, tracked_files, project_path,
                                    content_hash=new_hash,
                                    last_hash=last_content_hash,
                                )
                                if result:
                                    log("API sync ✓")
                                    _update_ai_state(result)
                                else:
                                    log("API sync ✗")
                            except SyncError as e:
                                if e.code == "SESSION_PAUSED":
                                    session_status = "paused"
                                    log("⏸ Aula pausada — sync suspenso")
                                elif e.code == "SESSION_ENDED":
                                    session_status = "ended"
                                    log("🔴 Aula encerrada — encerrando monitoramento")
                                    running = False
                                elif e.code == "NO_SESSION":
                                    session_status = None
                                    log("⚠ Nenhuma aula ativa — aguardando...")
                                else:
                                    log(f"⚠ {e}")

                        last_content_hash = new_hash

                # Refresh TUI
                live.update(
                    build_dashboard(
                        version=__version__,
                        class_id=config.class_id,
                        class_name=config.class_name,
                        project_path=str(project_path),
                        mode=mode,
                        tracked_files=tracked_files,
                        dirty_count=len(handler.dirty_files),
                        ai_score=ai_score,
                        ai_summary=ai_summary,
                        ai_issues=ai_issues,
                        ai_positives=ai_positives,
                        session_title=session_title,
                        session_status=session_status,
                        log_lines=log_lines,
                        teacher_last_publish_at=teacher_last_publish_at,
                        teacher_files_published=teacher_files_published,
                        teacher_blob_bytes=teacher_blob_bytes,
                    )
                )

    finally:
        observer.stop()
        observer.join()
        console.print("\n👋 [dim]MonitorIA encerrado.[/dim]\n")
