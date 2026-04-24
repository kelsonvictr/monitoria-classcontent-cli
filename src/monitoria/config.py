"""Local configuration management for MonitorIA."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

CONFIG_DIR = Path.home() / ".monitoria"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_API_URL = "https://tiq1rj8bui.execute-api.sa-east-1.amazonaws.com/dev"


@dataclass
class MonitoriaConfig:
    """Persistent local configuration."""

    token: str | None = None
    refresh_token: str | None = None
    class_id: str | None = None
    class_name: str | None = None
    api_url: str = DEFAULT_API_URL
    project_path: str | None = None
    last_sync_at: str | None = None
    device_id: str | None = None

    # File filter defaults
    extensions: list[str] = field(default_factory=lambda: [
        ".java", ".py", ".ts", ".tsx", ".js", ".jsx",
        ".html", ".css", ".xml", ".yml", ".yaml",
        ".json", ".sql", ".kt", ".scala", ".c", ".cpp", ".h",
    ])
    ignore_dirs: list[str] = field(default_factory=lambda: [
        "node_modules", ".git", "target", "build", "dist",
        "__pycache__", ".venv", "venv", ".idea", ".vscode",
        ".gradle", "bin", "obj", ".class",
    ])
    max_file_size_kb: int = 500
    debounce_seconds: int = 30

    @classmethod
    def load(cls) -> MonitoriaConfig:
        """Load config from ~/.monitoria/config.json or return defaults."""
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()

    def save(self) -> None:
        """Save config to ~/.monitoria/config.json."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def merge_project_config(self, project_path: Path) -> None:
        """Merge .monitoria.yml from project root if present."""
        import yaml

        yml_file = project_path / ".monitoria.yml"
        if yml_file.exists():
            try:
                data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    if "extensions" in data:
                        self.extensions = data["extensions"]
                    if "ignore" in data:
                        self.ignore_dirs = data["ignore"]
                    if "debounce_seconds" in data:
                        self.debounce_seconds = data["debounce_seconds"]
                    if "max_file_size_kb" in data:
                        self.max_file_size_kb = data["max_file_size_kb"]
            except Exception:
                pass
