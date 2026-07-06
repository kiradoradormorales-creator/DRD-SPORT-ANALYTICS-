from datetime import date, timedelta
import requests
from config import FOOTBALL_DATA_API_KEY, FOOTBALL_DATA_BASE_URL, CACHE_TTL_SECONDS
from cache.simple_cache import get_cache, set_cache

class FootballDataClient:
    def __init__(self):
        self.base_url = FOOTBALL_DATA_BASE_URL.rstrip("/")
        self.api_key = FOOTBALL_DATA_API_KEY

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _headers(self):
        return {"X-Auth-Token": self.api_key}

    def _get(self, path: str, params=None):
        if not self.enabled:
            raise RuntimeError("Falta FOOTBALL_DATA_API_KEY")
        params = params or {}
        key = f"GET:{path}:{sorted(params.items())}"
        cached = get_cache(key, CACHE_TTL_SECONDS)
        if cached is not None:
            return cached
        url = f"{self.base_url}{path}"
        r = requests.get(url, headers=self._headers(), params=params, timeout=20)
        if r.status_code == 403:
            raise RuntimeError("Token inválido o endpoint fuera del plan gratis.")
        if r.status_code == 429:
            raise RuntimeError("Límite de API alcanzado. Espera un rato o baja consultas.")
        r.raise_for_status()
        return set_cache(key, r.json())

    def status(self):
        if not self.enabled:
            return {"ok": False, "modo": "DEMO", "mensaje": "Sin API key: usando modo demo/local."}
        try:
            data = self._get("/competitions", {})
            return {"ok": True, "modo": "API", "mensaje": f"API conectada. Competiciones disponibles: {len(data.get('competitions', []))}"}
        except Exception as e:
            return {"ok": False, "modo": "DEMO", "mensaje": f"API no disponible: {e}. Usando modo demo."}

    def matches_by_date(self, d: date | None = None):
        d = d or date.today()
        data = self._get("/matches", {"dateFrom": d.isoformat(), "dateTo": d.isoformat()})
        return data.get("matches", [])

    def upcoming_matches(self, days: int = 7):
        start = date.today()
        end = start + timedelta(days=days)
        data = self._get("/matches", {"dateFrom": start.isoformat(), "dateTo": end.isoformat()})
        return data.get("matches", [])

    def team_matches(self, team_id: int, limit: int = 10, status: str = "FINISHED"):
        data = self._get(f"/teams/{team_id}/matches", {"status": status, "limit": limit})
        return data.get("matches", [])

    def head_to_head(self, match_id: int, limit: int = 10):
        data = self._get(f"/matches/{match_id}/head2head", {"limit": limit})
        return data.get("matches", [])

client = FootballDataClient()
