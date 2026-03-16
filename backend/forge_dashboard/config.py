"""DashboardConfig — centralised settings for the Forge Dashboard backend."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class DashboardConfig(BaseSettings):
    """Configuration loaded from environment variables prefixed with FORGE_DASHBOARD_."""

    model_config = {"env_prefix": "FORGE_DASHBOARD_"}

    crucible_root: Path = Path(".")
    cartographer_root: Path = Path(".")
    crossfire_root: Path = Path(".")
    bulwark_root: Path = Path(".")
    db_path: Path = Path(".forge-dashboard/state.db")
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    poll_interval: float = 2.0
