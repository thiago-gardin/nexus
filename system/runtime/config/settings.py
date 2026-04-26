from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_db_path() -> Path:
    return _repo_root() / ".nexus" / "nexus.db"


def _default_env() -> str:
    return os.getenv("NEXUS_ENV", "development")


def _default_version() -> str:
    return os.getenv("NEXUS_VERSION", "0.1.0")


def _default_db_path_from_env() -> Path:
    return Path(os.getenv("NEXUS_DB_PATH", str(_default_db_path()))).expanduser()


@dataclass(frozen=True, slots=True)
class Settings:
    db_path: Path = field(default_factory=_default_db_path_from_env)
    env: str = field(default_factory=_default_env)
    version: str = field(default_factory=_default_version)

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.db_path.as_posix()}"


settings = Settings()
