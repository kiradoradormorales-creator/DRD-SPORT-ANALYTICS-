import math

def poisson(k, lamb):
    return (math.exp(-lamb) * lamb**k) / math.factorial(k)

def calcular_xg_from_data(local_data, visitante_data):
    n_l = max(local_data.get("partidos_usados", 10), 1)
    n_v = max(visitante_data.get("partidos_usados", 10), 1)
    gf_l = local_data["gf"] / n_l
    gc_l = local_data["gc"] / n_l
    gf_v = visitante_data["gf"] / n_v
    gc_v = visitante_data["gc"] / n_v
    xg_l = (gf_l * 0.60 + gc_v * 0.40) * 1.08
    xg_v = (gf_v * 0.55 + gc_l * 0.45) * 0.94
    return round(max(0.2, min(xg_l, 4.5)), 2), round(max(0.2, min(xg_v, 4.5)), 2)

def calcular_resultado_y_goles(xg_l, xg_v, max_goals=6):
    p_local = p_empate = p_visitante = over15 = over25 = over35 = btts = 0
    marcadores = []
    for gl in range(max_goals + 1):
        for gv in range(max_goals + 1):
            p = poisson(gl, xg_l) * poisson(gv, xg_v)
            if gl > gv: p_local += p
            elif gl == gv: p_empate += p
            else: p_visitante += p
            if gl + gv > 1.5: over15 += p
            if gl + gv > 2.5: over25 += p
            if gl + gv > 3.5: over35 += p
            if gl > 0 and gv > 0: btts += p
            marcadores.append((f"{gl}-{gv}", round(p * 100, 2)))
    mercados = [
        ("Goles", "Más de 1.5 goles", round(over15 * 100, 1)),
        ("Goles", "Más de 2.5 goles", round(over25 * 100, 1)),
        ("Goles", "Menos de 3.5 goles", round((1-over35) * 100, 1)),
        ("BTTS", "Ambos anotan - Sí", round(btts * 100, 1)),
        ("BTTS", "Ambos anotan - No", round((1-btts) * 100, 1)),
    ]
    marcadores = sorted(marcadores, key=lambda x: x[1], reverse=True)[:8]
    return round(p_local*100,1), round(p_empate*100,1), round(p_visitante*100,1), mercados, marcadores

def calcular_mercados_extra(local_data, visitante_data):
    corners_total = round((local_data["corners_favor"] + visitante_data["corners_favor"] + local_data["corners_contra"] + visitante_data["corners_contra"]) / 20, 1)
    tarjetas_total = round((local_data["tarjetas"] + visitante_data["tarjetas"]) / 10, 1)
    faltas_total = round((local_data["faltas"] + visitante_data["faltas"]) / 10, 1)
    mercados = [
        ("Corners", "Más de 7.5 corners", min(92, round(50 + (corners_total-7.5)*8, 1))),
        ("Corners", "Más de 8.5 corners", min(88, round(45 + (corners_total-8.5)*8, 1))),
        ("Tarjetas", "Más de 2.5 tarjetas", min(90, round(48 + (tarjetas_total-2.5)*10, 1))),
        ("Tarjetas", "Menos de 5.5 tarjetas", max(35, round(78 - max(0, tarjetas_total-4.5)*12, 1))),
        ("Faltas", "Más de 20.5 faltas", min(89, round(45 + (faltas_total-20.5)*4, 1))),
    ]
    return mercados, corners_total, tarjetas_total, faltas_total
