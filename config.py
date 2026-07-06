from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

APP_NAME = "DRD SPORT ANALYTICS"
APP_VERSION = "v1.4.0 Streamlit Ultra"

ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ENV_PATH = ROOT_DIR / ".env"
HOME_ENV_DIR = Path.home() / ".drd_sport_analytics"
HOME_ENV_PATH = HOME_ENV_DIR / ".env"

# Carga .env local y global. OJO: luego _env() lee el archivo local primero,
# para que la key del proyecto gane sobre cualquier key vieja guardada en Windows.
load_dotenv(PROJECT_ENV_PATH, override=True)
load_dotenv(HOME_ENV_PATH, override=False)


def _read_env_value(path: Path, name: str) -> str:
    try:
        if not path.exists():
            return ""
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == name:
                return _clean_value(value)
    except Exception:
        return ""
    return ""


def _clean_value(value: str | None) -> str:
    value = (value or "").strip().strip('"').strip("'").strip()
    if value.upper().startswith("API_FOOTBALL_KEY="):
        value = value.split("=", 1)[1].strip().strip('"').strip("'").strip()
    return value


def _env(name: str, default: str = "") -> str:
    # Prioridad: .env local -> .env global -> variables del sistema -> default.
    return _clean_value(
        _read_env_value(PROJECT_ENV_PATH, name)
        or _read_env_value(HOME_ENV_PATH, name)
        or os.getenv(name, "")
        or default
    )


def _normalize_base_url(value: str) -> str:
    value = _clean_value(value) or "https://v3.football.api-sports.io"
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value.rstrip("/")


def _normalize_host(value: str) -> str:
    value = _clean_value(value) or "v3.football.api-sports.io"
    value = value.replace("https://", "").replace("http://", "").strip("/")
    return value


API_FOOTBALL_KEY = _env("API_FOOTBALL_KEY")
API_FOOTBALL_BASE_URL = _normalize_base_url(_env("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io"))
API_FOOTBALL_HOST = _normalize_host(_env("API_FOOTBALL_HOST", "v3.football.api-sports.io"))

FOOTBALL_DATA_API_KEY = _env("FOOTBALL_DATA_API_KEY")
FOOTBALL_DATA_BASE_URL = _normalize_base_url(_env("FOOTBALL_DATA_BASE_URL", "https://api.football-data.org/v4"))

CACHE_TTL_SECONDS = int(_env("CACHE_TTL_SECONDS", "900") or "900")
TEMPORADA_DEFAULT = int(_env("TEMPORADA_DEFAULT", "2025") or "2025")


def save_api_key(api_key: str, save_global: bool = True) -> Path:
    clean_key = _clean_value(api_key)
    if not clean_key:
        raise ValueError("La API key está vacía.")

    target = HOME_ENV_PATH if save_global else PROJECT_ENV_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"API_FOOTBALL_KEY={clean_key}",
        "API_FOOTBALL_HOST=v3.football.api-sports.io",
        "API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io",
        f"CACHE_TTL_SECONDS={CACHE_TTL_SECONDS}",
        f"TEMPORADA_DEFAULT={TEMPORADA_DEFAULT}",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if save_global and not PROJECT_ENV_PATH.exists():
        PROJECT_ENV_PATH.write_text(
            "# DRD lee la key global desde ~/.drd_sport_analytics/.env\n"
            "# Si quieres usar una key distinta solo para este proyecto, pega aquí:\n"
            "# API_FOOTBALL_KEY=tu_key\n",
            encoding="utf-8",
        )
    return target


def masked_key() -> str:
    if not API_FOOTBALL_KEY:
        return ""
    if len(API_FOOTBALL_KEY) <= 8:
        return "*" * len(API_FOOTBALL_KEY)
    return API_FOOTBALL_KEY[:4] + "…" + API_FOOTBALL_KEY[-4:]


def admin_mode_enabled() -> bool:
    return _env("DRD_ADMIN_MODE", "0").lower() in ("1", "true", "yes", "si", "sí")
