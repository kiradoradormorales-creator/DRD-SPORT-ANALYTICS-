from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any
import re

from api.api_football_client import client
from datos.equipos_demo import EQUIPOS_DEMO

TEAM_EMOJIS = {
    "Spain":"🇪🇸", "Austria":"🇦🇹", "Portugal":"🇵🇹", "Croatia":"🇭🇷", "Brazil":"🇧🇷", "Norway":"🇳🇴",
    "Mexico":"🇲🇽", "England":"🏴", "Argentina":"🇦🇷", "France":"🇫🇷", "Switzerland":"🇨🇭", "Algeria":"🇩🇿",
    "Colombia":"🇨🇴", "Germany":"🇩🇪", "Belgium":"🇧🇪", "Morocco":"🇲🇦", "United States":"🇺🇸",
    "Saudi Arabia":"🇸🇦", "Ivory Coast":"🇨🇮", "Japan":"🇯🇵", "Morocco":"🇲🇦", "Canada":"🇨🇦",
}

NAME_ES = {
    "Spain":"España", "Austria":"Austria", "Portugal":"Portugal", "Croatia":"Croacia", "Brazil":"Brasil", "Norway":"Noruega",
    "Mexico":"México", "England":"Inglaterra", "Argentina":"Argentina", "France":"Francia", "Switzerland":"Suiza", "Algeria":"Argelia",
    "Colombia":"Colombia", "Germany":"Alemania", "Belgium":"Bélgica", "Morocco":"Marruecos", "United States":"Estados Unidos",
    "Saudi Arabia":"Arabia Saudita", "Ivory Coast":"Costa de Marfil", "Japan":"Japón", "Canada":"Canadá", "Australia":"Australia",
    "Egypt":"Egipto", "Ghana":"Ghana", "Cape Verde":"Cabo Verde", "DR Congo":"RD Congo", "Paraguay":"Paraguay",
    "Sweden":"Suecia", "Netherlands":"Países Bajos", "Turkey":"Turquía", "Qatar":"Qatar", "Bosnia and Herzegovina":"Bosnia y Herzegovina",
}

_LAST_API_ERROR = ""
_LAST_API_META: dict[str, Any] = {}


SEARCH_ALIASES = {
    "mundial": ["world cup", "fifa", "copa mundial"],
    "copa mundial": ["world cup", "fifa"],
    "selecciones": ["world cup", "international", "friendly", "qualification"],
    "champions": ["champions league", "uefa champions"],
    "liga mx": ["liga mx", "mexico"],
    "mexico": ["mexico", "liga mx", "méxico"],
    "espana": ["spain", "españa"],
    "españa": ["spain", "españa"],
    "austria": ["austria"],
    "egipto": ["egypt", "egipto"],
}

TEAM_PRIORS = {
    # Selecciones fuertes / Mundial. Estos valores NO son datos inventados de API;
    # son priors DRD para no romper análisis cuando el plan Free no entrega últimos partidos.
    "Spain": 92, "France": 91, "Argentina": 91, "England": 89, "Brazil": 89, "Portugal": 88,
    "Germany": 87, "Netherlands": 86, "Belgium": 84, "Croatia": 83, "Uruguay": 82, "Colombia": 81,
    "Morocco": 79, "Mexico": 78, "Switzerland": 78, "United States": 77, "Japan": 77, "Austria": 76,
    "Denmark": 76, "Norway": 75, "Sweden": 75, "Senegal": 75, "Australia": 71, "Egypt": 72,
    "Algeria": 72, "Ivory Coast": 72, "Ghana": 71, "Paraguay": 70, "Canada": 70, "Turkey": 73,
    "Saudi Arabia": 66, "Qatar": 64, "Cape Verde": 64, "DR Congo": 66,
}

IMPORTANT_LEAGUE_HINTS = (
    "world cup", "fifa", "uefa", "champions", "europa", "conference",
    "premier", "laliga", "la liga", "serie a", "bundesliga", "ligue 1",
    "liga mx", "mls", "libertadores", "sudamericana", "nations",
)


def _norm_text(value: str) -> str:
    value = (value or "").lower()
    repl = {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u", "ü":"u", "ñ":"n"}
    for a, b in repl.items():
        value = value.replace(a, b)
    return value


def search_terms(query: str) -> list[str]:
    q = _norm_text(query).strip()
    if not q:
        return []
    terms = [q]
    terms.extend(_norm_text(x) for x in SEARCH_ALIASES.get(q, []))
    # Búsqueda flexible por palabras comunes.
    if "world" in q or "mundial" in q:
        terms.extend(["world cup", "fifa"])
    return list(dict.fromkeys(t for t in terms if t))


def match_search_text(match: dict) -> str:
    home, away = get_match_teams(match)
    league = match.get("league", match.get("competition", {}))
    parts = [
        home.get("name", ""), away.get("name", ""),
        league.get("name", ""), league.get("country", ""), league.get("round", ""),
        match.get("fixture", {}).get("status", {}).get("long", ""),
        match_label(match),
    ]
    return _norm_text(" ".join(str(x) for x in parts))


def filtrar_matches(matches: list[dict], query: str) -> list[dict]:
    terms = search_terms(query)
    if not terms:
        return matches
    out = [m for m in matches if any(t in match_search_text(m) for t in terms)]
    return out


def ordenar_partidos_utiles(matches: list[dict]) -> list[dict]:
    def score(m: dict):
        league_name = _norm_text(m.get("league", {}).get("name", ""))
        country = _norm_text(m.get("league", {}).get("country", ""))
        status = m.get("fixture", {}).get("status", {}).get("short", "")
        base = 0
        if any(h in league_name or h in country for h in IMPORTANT_LEAGUE_HINTS):
            base += 1000
        if "world cup" in league_name or "fifa" in league_name:
            base += 3000
        if status in ("NS", "TBD"):
            base += 100
        return (-base, _sort_key(m))
    return sorted(matches, key=score)



def _set_api_error(message: str) -> None:
    global _LAST_API_ERROR
    _LAST_API_ERROR = message or ""


def ultimo_error_api() -> str:
    return _LAST_API_ERROR


def ultima_meta_api() -> dict[str, Any]:
    return dict(_LAST_API_META)


def estado_fuente():
    return client.status()


def _fecha_fixture(match: dict) -> str:
    return match.get("fixture", {}).get("date") or match.get("utcDate", "") or ""


def _parse_fecha(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _sort_key(match: dict):
    parsed = _parse_fecha(_fecha_fixture(match))
    return parsed or datetime.max


def _unique_matches(matches: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for m in matches:
        fid = m.get("fixture", {}).get("id") or m.get("id") or match_label(m)
        if fid in seen:
            continue
        seen.add(fid)
        out.append(m)
    return out


def _extraer_ventana_free_plan(error_text: str) -> tuple[date, date] | None:
    """API-Sports free a veces limita fechas y devuelve: try from YYYY-MM-DD to YYYY-MM-DD."""
    if not error_text:
        return None
    m = re.search(r"from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", error_text, re.IGNORECASE)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1)), date.fromisoformat(m.group(2))
    except ValueError:
        return None


def _filtrar_partidos(matches: list[dict], incluir_finalizados: bool) -> list[dict]:
    matches = _unique_matches(matches)
    if not incluir_finalizados:
        live_or_upcoming = [
            m for m in matches
            if m.get("fixture", {}).get("status", {}).get("short") not in ("FT", "AET", "PEN", "CANC", "ABD", "PST")
        ]
        matches = live_or_upcoming or matches
    return sorted(matches, key=_sort_key)


def _consultar_por_dias(start: date, end: date) -> list[dict]:
    matches: list[dict] = []
    total_days = max((end - start).days, 0)
    for offset in range(total_days + 1):
        d = start + timedelta(days=offset)
        daily = client.fixtures_by_date(d)
        if daily:
            matches.extend(daily)
    return matches


def partidos_disponibles(days: int = 7, incluir_finalizados: bool = False) -> list[dict]:
    """Devuelve fixtures reales desde API-Football.

    Compatible con plan Free: si API-Sports responde que solo permite una ventana
    concreta (ej. 2026-07-02 a 2026-07-04), DRD cambia automáticamente a esa
    ventana para no caer en demo.
    """
    global _LAST_API_META
    _LAST_API_META = {}
    _set_api_error("")

    if not client.enabled:
        _set_api_error("No hay API_FOOTBALL_KEY cargada.")
        return []

    today = date.today()
    window_days = max(int(days), 1)
    requested_until = today + timedelta(days=window_days)

    try:
        matches = _consultar_por_dias(today, requested_until)
        matches = ordenar_partidos_utiles(_filtrar_partidos(matches, incluir_finalizados))
        _LAST_API_META = {
            "from": today.isoformat(),
            "to": requested_until.isoformat(),
            "count": len(matches),
            "base_url": getattr(client, "base_url", ""),
            "auto_window": False,
        }
        if not matches:
            _set_api_error(f"API conectada, pero no devolvió fixtures entre {today.isoformat()} y {requested_until.isoformat()}.")
        return matches

    except Exception as e:
        original_error = str(e)
        allowed = _extraer_ventana_free_plan(original_error)
        if not allowed:
            _set_api_error(original_error)
            return []

        # Plan Free: API-Sports nos dice qué fechas sí permite. Usamos esas fechas.
        allowed_from, allowed_to = allowed
        try:
            matches = _consultar_por_dias(allowed_from, allowed_to)
            matches = ordenar_partidos_utiles(_filtrar_partidos(matches, incluir_finalizados))
            _LAST_API_META = {
                "from": allowed_from.isoformat(),
                "to": allowed_to.isoformat(),
                "count": len(matches),
                "base_url": getattr(client, "base_url", ""),
                "auto_window": True,
                "requested_from": today.isoformat(),
                "requested_to": requested_until.isoformat(),
            }
            if matches:
                _set_api_error(
                    f"Plan Free: API-Sports no permitió {today.isoformat()} → {requested_until.isoformat()}. "
                    f"DRD cargó automáticamente la ventana permitida {allowed_from.isoformat()} → {allowed_to.isoformat()}."
                )
            else:
                _set_api_error(
                    f"Plan Free permitió {allowed_from.isoformat()} → {allowed_to.isoformat()}, "
                    "pero no devolvió fixtures en esa ventana."
                )
            return matches
        except Exception as second_error:
            _set_api_error(f"Error inicial: {original_error}. Error al intentar ventana Free: {second_error}")
            return []


def partidos_demo():
    names = list(EQUIPOS_DEMO.keys())
    preferred = [("España", "Austria"), ("Portugal", "Croacia"), ("Brasil", "Noruega"), ("México", "Inglaterra"), ("Argentina", "Argelia")]
    base = []
    for i, (h, a) in enumerate(preferred):
        if h in EQUIPOS_DEMO and a in EQUIPOS_DEMO:
            base.append({
                "demo": True,
                "fixture": {"id": f"demo-{i}", "date": "Modo local", "status": {"short": "NS", "long": "Demo"}},
                "league": {"name": "Demo DRD"},
                "teams": {"home": {"id": f"demo-h-{i}", "name": h}, "away": {"id": f"demo-a-{i}", "name": a}},
            })
    if base:
        return base
    for i in range(0, len(names)-1, 2):
        base.append({"demo": True, "fixture": {"id": f"demo-{i}", "date": "Modo local", "status": {"short": "NS"}}, "league": {"name": "Demo DRD"}, "teams": {"home": {"name": names[i]}, "away": {"name": names[i+1]}}})
    return base


def pretty_team_name(api_name: str):
    return NAME_ES.get(api_name, api_name)


def team_label(team: dict):
    name = team.get("name", "Equipo")
    emoji = TEAM_EMOJIS.get(name, "⚽")
    return f"{emoji} {pretty_team_name(name)}"


def get_match_teams(match: dict):
    if "teams" in match:
        return match["teams"]["home"], match["teams"]["away"]
    return match["homeTeam"], match["awayTeam"]


def match_label(match: dict):
    home, away = get_match_teams(match)
    league = match.get("league", match.get("competition", {})).get("name", "Competición")
    when = _fecha_fixture(match)
    status = match.get("fixture", {}).get("status", {}).get("short", "")
    return f"{team_label(home)} vs {team_label(away)} · {league} · {when[:16]} · {status}"


def _result_for_team(team_id: int, fixture: dict):
    teams = fixture.get("teams", {})
    goals = fixture.get("goals", {})
    home = teams.get("home", {})
    away = teams.get("away", {})
    hg, ag = goals.get("home"), goals.get("away")
    if hg is None or ag is None:
        return None
    is_home = home.get("id") == team_id
    gf, gc = (hg, ag) if is_home else (ag, hg)
    res = "G" if gf > gc else "E" if gf == gc else "P"
    return gf, gc, res, "home" if is_home else "away"


def _build_stats_from_api_football(team_name: str, team_id: int, fixtures: list[dict]):
    gf = gc = 0
    forma = []
    home_gf = home_gc = home_n = away_gf = away_gc = away_n = 0
    for f in fixtures:
        r = _result_for_team(team_id, f)
        if not r:
            continue
        a, b, res, loc = r
        gf += a; gc += b; forma.append(res)
        if loc == "home":
            home_gf += a; home_gc += b; home_n += 1
        else:
            away_gf += a; away_gc += b; away_n += 1
    n = max(len(forma), 1)
    puntos = sum(3 if x == "G" else 1 if x == "E" else 0 for x in forma)
    ritmo = max(0.70, min(1.40, (gf + gc) / max(n * 2.45, 1)))
    return {
        "id": team_id,
        "emoji": TEAM_EMOJIS.get(team_name, "⚽"),
        "gf": gf,
        "gc": gc,
        "forma": forma or ["E"] * 5,
        "corners_favor": round((43 + gf * 1.1) * ritmo),
        "corners_contra": round((39 + gc * 1.0) * ritmo),
        "tarjetas": round(15 + n * 1.25 + max(0, gc - gf) * .45),
        "faltas": round(95 + n * 2.4 + max(0, gc - gf) * 1.6),
        "puntos_forma": puntos,
        "partidos_usados": n,
        "home_avg_gf": home_gf / home_n if home_n else gf / n,
        "home_avg_gc": home_gc / home_n if home_n else gc / n,
        "away_avg_gf": away_gf / away_n if away_n else gf / n,
        "away_avg_gc": away_gc / away_n if away_n else gc / n,
        "fuente": "API-Football",
    }


def _prior_stats_from_name(api_name: str, team_id: int | str | None = None) -> dict:
    """Fallback honesto: usa el fixture real de API y un rating DRD cuando Free no entrega historial.

    Esto evita el error rojo en partidos reales como World Cup donde el plan Free muestra
    fixtures pero no siempre permite últimos partidos/estadísticas. No lo marcamos como
    estadística real pura: la fuente será API-Football + estimación DRD.
    """
    rating = TEAM_PRIORS.get(api_name, 68)
    # Rating 68 ~ equipo medio. 92 ~ elite. Lo convertimos a 10 partidos sintéticos.
    attack = max(7, min(28, round((rating - 50) * 0.42 + 10)))
    defense_allowed = max(5, min(22, round(22 - (rating - 50) * 0.25)))
    wins = max(1, min(8, round((rating - 52) / 8)))
    draws = max(1, min(4, round(4 - abs(rating - 72) / 16)))
    losses = max(1, 10 - wins - draws)
    forma = (["G"] * wins + ["E"] * draws + ["P"] * losses)[:10]
    # Métricas auxiliares para que el motor pueda trabajar aunque API Free no entregue corners/tarjetas.
    return {
        "id": team_id or api_name,
        "emoji": TEAM_EMOJIS.get(api_name, "⚽"),
        "gf": attack,
        "gc": defense_allowed,
        "forma": forma or ["E"] * 5,
        "corners_favor": round(38 + (rating - 60) * 0.55),
        "corners_contra": round(42 - (rating - 65) * 0.35),
        "tarjetas": round(25 + max(0, 72 - rating) * 0.25),
        "faltas": round(108 + max(0, 72 - rating) * 0.65),
        "puntos_forma": wins * 3 + draws,
        "partidos_usados": 10,
        "home_avg_gf": attack / 10,
        "home_avg_gc": defense_allowed / 10,
        "away_avg_gf": attack / 10,
        "away_avg_gc": defense_allowed / 10,
        "rating_drd": rating,
        "fuente": "API-Football + estimación DRD",
    }


def _enough_history(fixtures: list[dict], team_id: int) -> bool:
    completed = 0
    for f in fixtures:
        if _result_for_team(team_id, f):
            completed += 1
    return completed >= 3


def obtener_stats_api_o_demo(home: dict, away: dict, match: dict | None = None):
    hname_api = home.get("name", "")
    aname_api = away.get("name", "")
    hname = pretty_team_name(hname_api)
    aname = pretty_team_name(aname_api)

    if str(home.get("id", "")).startswith("demo") or not client.enabled:
        return EQUIPOS_DEMO.get(hname), EQUIPOS_DEMO.get(aname), "DEMO"

    try:
        hid = int(home["id"])
        aid = int(away["id"])
    except Exception:
        return _prior_stats_from_name(hname_api, home.get("id")), _prior_stats_from_name(aname_api, away.get("id")), "API-Football + estimación DRD"

    errors: list[str] = []
    h = a = None
    try:
        hm = client.last_fixtures(hid, last=10)
        if _enough_history(hm, hid):
            h = _build_stats_from_api_football(hname_api, hid, hm)
        else:
            errors.append(f"{hname}: historial insuficiente en plan Free")
    except Exception as e:
        errors.append(f"{hname}: {e}")

    try:
        am = client.last_fixtures(aid, last=10)
        if _enough_history(am, aid):
            a = _build_stats_from_api_football(aname_api, aid, am)
        else:
            errors.append(f"{aname}: historial insuficiente en plan Free")
    except Exception as e:
        errors.append(f"{aname}: {e}")

    if h and a:
        return h, a, "API-Football"

    # Si uno o ambos equipos no tienen historial accesible, no matamos el análisis.
    # Usamos el partido real + rating DRD para generar una lectura útil, marcada como estimada.
    if h is None:
        h = _prior_stats_from_name(hname_api, hid)
    if a is None:
        a = _prior_stats_from_name(aname_api, aid)
    if errors:
        _set_api_error(" | ".join(errors[:3]))
    return h, a, "API-Football + estimación DRD"
