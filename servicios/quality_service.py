from __future__ import annotations

from typing import Any


def _is_estimated(source: str) -> bool:
    text = (source or "").lower()
    return "estim" in text or "demo" in text


def _public_source_name(source: str) -> str:
    text = (source or "").lower()
    if "demo" in text:
        return "Lectura demo"
    if "estim" in text:
        return "Lectura exploratoria"
    if "api" in text:
        return "Lectura con datos disponibles"
    return "Lectura DRD"


def _history_points(data: dict[str, Any]) -> int:
    n = int(data.get("partidos_usados", 0) or 0)
    if n >= 10:
        return 25
    if n >= 6:
        return 18
    if n >= 3:
        return 10
    return 0


def evaluar_calidad_analisis(
    data_local: dict[str, Any],
    data_visitante: dict[str, Any],
    fuente: str,
    match: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evalúa si el análisis puede presentarse como fuerte o solo exploratorio.

    Esta capa está pensada para usuarios normales: evita palabras técnicas como API,
    fixture, priors o Poisson en la interfaz pública. Los detalles técnicos se quedan
    para el modo administrador.
    """
    match = match or {}
    estimated = _is_estimated(fuente)
    demo = "demo" in (fuente or "").lower()

    fixture_ok = bool(match.get("fixture", {}).get("id")) and not match.get("demo")
    league_ok = bool(match.get("league", {}).get("name") or match.get("competition", {}).get("name"))
    teams_ok = bool(match.get("teams") or (match.get("homeTeam") and match.get("awayTeam")))
    status_ok = bool(match.get("fixture", {}).get("status") or match.get("status"))
    venue_ok = bool(match.get("fixture", {}).get("venue", {}).get("name"))

    hist_l = int(data_local.get("partidos_usados", 0) or 0)
    hist_v = int(data_visitante.get("partidos_usados", 0) or 0)
    history_ok = (hist_l >= 3 and hist_v >= 3 and not estimated)

    h2h_ok = bool(match.get("drd_h2h_ok"))
    corners_real = bool(data_local.get("corners_reales") and data_visitante.get("corners_reales"))
    cards_real = bool(data_local.get("tarjetas_reales") and data_visitante.get("tarjetas_reales"))
    lineups_ok = bool(match.get("drd_lineups_ok"))
    injuries_ok = bool(match.get("drd_injuries_ok"))

    score = 0
    score += 15 if fixture_ok else 0
    score += 10 if league_ok else 0
    score += 10 if teams_ok else 0
    score += 5 if status_ok else 0
    score += 5 if venue_ok else 0
    score += _history_points(data_local)
    score += _history_points(data_visitante)
    score += 8 if h2h_ok else 0
    score += 6 if corners_real else 0
    score += 6 if cards_real else 0
    score += 5 if lineups_ok else 0
    score += 5 if injuries_ok else 0

    if estimated:
        score = min(score, 48)
    if demo:
        score = min(score, 35)
    score = max(0, min(100, int(score)))

    if score >= 85:
        nivel = "Alta"
        color = "🟢"
        public_status = "Análisis fuerte"
        user_action = "Puede servir como una lectura principal, siempre con gestión de riesgo."
    elif score >= 60:
        nivel = "Media"
        color = "🟡"
        public_status = "Análisis útil"
        user_action = "Úsalo como apoyo, no como única razón para decidir."
    elif score >= 40:
        nivel = "Parcial"
        color = "🟠"
        public_status = "Lectura exploratoria"
        user_action = "Solo referencia. DRD no recomienda decisiones fuertes con esta información."
    else:
        nivel = "Baja"
        color = "🔴"
        public_status = "Datos insuficientes"
        user_action = "Mejor pasar este partido o buscar otro con más información disponible."

    verified = score >= 85 and not estimated and history_ok
    # DRD no oculta valor al usuario: siempre puede mostrar una lectura,
    # pero cambia el lenguaje según la calidad de datos.
    # La honestidad está en etiquetar la lectura como fuerte, útil o exploratoria.
    can_show_recommendations = not demo
    can_show_probabilities = not demo

    available = []
    missing = []

    def add(name: str, ok: bool, why: str = ""):
        item = {"nombre": name, "ok": ok, "detalle": why}
        (available if ok else missing).append(item)

    add("Partido confirmado", fixture_ok, "El partido existe en la fuente de datos.")
    add("Competición identificada", league_ok, "Se conoce la liga o torneo.")
    add("Equipos identificados", teams_ok, "Local y visitante están claros.")
    add("Estado y horario", status_ok, "Hay estado/horario del partido.")
    add("Sede / estadio", venue_ok, "La sede aparece en la cobertura.")
    add("Historial reciente", history_ok, "Hay partidos recientes suficientes.")
    add("Enfrentamientos directos", h2h_ok, "Hay historial directo entre equipos.")
    add("Corners confiables", corners_real, "Hay datos reales de corners.")
    add("Tarjetas confiables", cards_real, "Hay datos reales de tarjetas.")
    add("Alineaciones", lineups_ok, "Hay alineaciones o posibles alineaciones.")
    add("Bajas / lesiones", injuries_ok, "Hay información de bajas.")

    if estimated:
        mensaje = "Este partido tiene información limitada. DRD muestra una lectura exploratoria, no una recomendación fuerte."
    elif verified:
        mensaje = "DRD Verified: hay suficiente información para una lectura fuerte y transparente."
    elif score >= 60:
        mensaje = "La lectura es útil, pero todavía faltan algunas capas importantes de información."
    else:
        mensaje = "No hay información suficiente para vender esto como análisis fuerte. Mejor usarlo solo como referencia."

    public_checks = available + missing
    technical_checks = [
        {"clave": "fixture", "nombre": "Fixture ID", "ok": fixture_ok, "tipo": "oficial"},
        {"clave": "league", "nombre": "Liga / competición", "ok": league_ok, "tipo": "oficial"},
        {"clave": "teams", "nombre": "Equipos", "ok": teams_ok, "tipo": "oficial"},
        {"clave": "history", "nombre": f"Historial reciente ({hist_l}/{hist_v})", "ok": history_ok, "tipo": "oficial"},
        {"clave": "h2h", "nombre": "H2H", "ok": h2h_ok, "tipo": "oficial"},
        {"clave": "corners", "nombre": "Corners reales", "ok": corners_real, "tipo": "oficial"},
        {"clave": "cards", "nombre": "Tarjetas reales", "ok": cards_real, "tipo": "oficial"},
        {"clave": "lineups", "nombre": "Alineaciones", "ok": lineups_ok, "tipo": "oficial"},
        {"clave": "injuries", "nombre": "Lesiones", "ok": injuries_ok, "tipo": "oficial"},
    ]

    model_components = [
        {"nombre": "Probabilidad de goles", "ok": True},
        {"nombre": "Forma reciente", "ok": hist_l >= 3 and hist_v >= 3},
        {"nombre": "Localía", "ok": True},
        {"nombre": "Índice DRD", "ok": True},
        {"nombre": "Estimación por falta de datos", "ok": estimated},
    ]

    return {
        "score": score,
        "nivel": nivel,
        "color": color,
        "public_status": public_status,
        "user_action": user_action,
        "verified": verified,
        "estimated": estimated,
        "demo": demo,
        "can_show_recommendations": can_show_recommendations,
        "can_show_probabilities": can_show_probabilities,
        "mensaje": mensaje,
        "available": available,
        "missing": missing,
        "public_checks": public_checks,
        "checks": technical_checks,
        "model_components": model_components,
        "public_source": _public_source_name(fuente),
    }
