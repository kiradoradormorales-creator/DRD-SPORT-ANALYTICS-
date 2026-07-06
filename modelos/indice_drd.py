def _forma_pts(forma):
    return sum(3 if x in ["G", "W"] else 1 if x in ["E", "D"] else 0 for x in forma[-10:])

def indice_drd(data, xg):
    n = max(data.get("partidos_usados", 10), 1)
    ataque = min(100, round((data["gf"] / n) * 38, 1))
    defensa = max(0, round(100 - (data["gc"] / n) * 35, 1))
    forma = round((_forma_pts(data["forma"]) / max(len(data["forma"])*3, 1)) * 100, 1)
    ritmo = min(100, round((data["corners_favor"] / max(n,1)) * 12, 1))
    xg_score = min(100, round(xg * 35, 1))
    total = round(ataque*.28 + defensa*.22 + forma*.22 + ritmo*.10 + xg_score*.18, 1)
    return {"Ataque": ataque, "Defensa": defensa, "Forma": forma, "Ritmo": ritmo, "xG": xg_score, "Índice DRD": total}

def nivel_indice(v):
    if v >= 80: return "🔥 Elite"
    if v >= 68: return "🟢 Fuerte"
    if v >= 55: return "🟡 Competitivo"
    return "🔴 Bajo"

def confianza_general(p_local, p_empate, p_visitante, mercados, xg_l, xg_v):
    mayor = max(p_local, p_empate, p_visitante)
    top = mercados[0][2] if mercados else 50
    diff_xg = abs(xg_l - xg_v)
    score = round(min(95, max(35, mayor*.55 + top*.30 + diff_xg*12)), 0)
    if score >= 75: return int(score), "Alta", "🟢"
    if score >= 60: return int(score), "Media", "🟡"
    return int(score), "Baja", "🔴"
