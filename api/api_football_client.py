from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import urlparse

import requests

from cache.simple_cache import get_cache, set_cache
from config import API_FOOTBALL_BASE_URL, API_FOOTBALL_KEY, API_FOOTBALL_HOST, CACHE_TTL_SECONDS


def _clean_key(value: str | None) -> str:
    raw = (value or "").strip().strip('"').strip("'").strip()
    if raw.upper().startswith("API_FOOTBALL_KEY="):
        raw = raw.split("=", 1)[1].strip().strip('"').strip("'").strip()
    return raw


def _is_rapidapi(base_url: str) -> bool:
    host = urlparse(base_url).netloc.lower()
    return "rapidapi" in host or "p.rapidapi.com" in host


class APIFootballClient:
    """Cliente único para API-Football.

    Modo API-Sports directo:
        API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
        Header: x-apisports-key

    Modo RapidAPI:
        API_FOOTBALL_BASE_URL=https://api-football-v1.p.rapidapi.com/v3
        Headers: x-rapidapi-key + x-rapidapi-host
    """

    def __init__(self) -> None:
        self.api_key = _clean_key(API_FOOTBALL_KEY)
        self.base_url = (API_FOOTBALL_BASE_URL or "https://v3.football.api-sports.io").rstrip("/")
        self.host = (API_FOOTBALL_HOST or urlparse(self.base_url).netloc).replace("https://", "").replace("http://", "").strip("/")
        self.timeout = 25
        self.rapidapi = _is_rapidapi(self.base_url)

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    @property
    def headers(self) -> dict[str, str]:
        if not self.api_key:
            return {"Accept": "application/json"}
        if self.rapidapi:
            host = self.host if "rapidapi" in self.host else "api-football-v1.p.rapidapi.com"
            return {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": host,
                "Accept": "application/json",
            }
        return {
            "x-apisports-key": self.api_key,
            "Accept": "application/json",
        }

    def _cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        return f"apifootball:{self.base_url}:{endpoint}:{sorted(params.items())}"

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("Falta API_FOOTBALL_KEY. Guárdala en Configuración o en .env.")

        clean_endpoint = endpoint.strip("/")
        clean_params = params or {}
        cache_key = self._cache_key(clean_endpoint, clean_params)

        cached = get_cache(cache_key, CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        url = f"{self.base_url}/{clean_endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=clean_params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise RuntimeError(f"No se pudo conectar con API-Football: {exc}") from exc

        text_preview = response.text[:500]
        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code in (401, 403):
            raise RuntimeError(
                "API key inválida o no enviada. Revisa .env: API_FOOTBALL_KEY=tu_key. "
                "Para API-Sports directo usa API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io. "
                "Para RapidAPI usa API_FOOTBALL_BASE_URL=https://api-football-v1.p.rapidapi.com/v3. "
                f"Respuesta: {text_preview}"
            )
        if response.status_code == 429:
            raise RuntimeError("Límite de consultas alcanzado. Espera o revisa tu plan.")
        if response.status_code >= 400:
            raise RuntimeError(f"Error HTTP {response.status_code}: {text_preview}")

        if not isinstance(data, dict):
            raise RuntimeError(f"API-Football no devolvió JSON válido: {text_preview}")

        errors = data.get("errors")
        if errors:
            msg = str(errors)
            raise RuntimeError(
                "API-Football respondió error. "
                f"Base URL usada: {self.base_url}. "
                f"Modo: {'RapidAPI' if self.rapidapi else 'API-Sports directo'}. "
                f"Detalle: {msg}"
            )

        return set_cache(cache_key, data)

    def status(self) -> dict[str, Any]:
        if not self.enabled:
            return {
                "ok": False,
                "modo": "DEMO",
                "mensaje": "Sin API_FOOTBALL_KEY: usando demo local.",
            }
        try:
            data = self._get("status")
            response = data.get("response", {})
            account = response.get("account", {})
            requests_info = response.get("requests", {})
            used = requests_info.get("current", "?")
            limit = requests_info.get("limit_day", "?")
            plan = account.get("plan", "Free") or "Free"
            return {
                "ok": True,
                "modo": "API-FOOTBALL",
                "mensaje": f"API-Football conectada. Plan: {plan}. Consultas hoy: {used}/{limit}.",
                "raw": response,
            }
        except Exception as exc:
            return {
                "ok": False,
                "modo": "DEMO",
                "mensaje": f"API no disponible: {exc}. Usando demo.",
            }

    def fixtures_by_date(self, d: date) -> list[dict[str, Any]]:
        data = self._get("fixtures", {"date": d.isoformat()})
        return data.get("response", [])

    def fixtures_between(self, date_from: date, date_to: date) -> list[dict[str, Any]]:
        data = self._get("fixtures", {"from": date_from.isoformat(), "to": date_to.isoformat()})
        return data.get("response", [])

    def last_fixtures(self, team_id: int, last: int = 10) -> list[dict[str, Any]]:
        data = self._get("fixtures", {"team": team_id, "last": last})
        return data.get("response", [])

    def h2h(self, team1: int, team2: int, last: int = 10) -> list[dict[str, Any]]:
        data = self._get("fixtures/headtohead", {"h2h": f"{team1}-{team2}", "last": last})
        return data.get("response", [])

    def fixture_statistics(self, fixture_id: int) -> list[dict[str, Any]]:
        data = self._get("fixtures/statistics", {"fixture": fixture_id})
        return data.get("response", [])

    def odds(self, fixture_id: int) -> list[dict[str, Any]]:
        data = self._get("odds", {"fixture": fixture_id})
        return data.get("response", [])


client = APIFootballClient()
