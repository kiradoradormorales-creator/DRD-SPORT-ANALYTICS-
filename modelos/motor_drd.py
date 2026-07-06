from modelos.poisson import calcular_xg_from_data, calcular_resultado_y_goles, calcular_mercados_extra
from modelos.indice_drd import indice_drd, confianza_general

def analizar_partido(local_name, visitante_name, data_local, data_visitante, fuente="DEMO"):
    xg_l, xg_v = calcular_xg_from_data(data_local, data_visitante)
    p_local, p_empate, p_visitante, mercados_goles, marcadores = calcular_resultado_y_goles(xg_l, xg_v)
    mercados_extra, corners_total, tarjetas_total, faltas_total = calcular_mercados_extra(data_local, data_visitante)

    ganador_local = ("1X2", f"Gana {local_name}", p_local)
    ganador_visitante = ("1X2", f"Gana {visitante_name}", p_visitante)
    doble_local = ("Doble oportunidad", f"{local_name} o empate", round(p_local + p_empate, 1))
    doble_visitante = ("Doble oportunidad", f"{visitante_name} o empate", round(p_visitante + p_empate, 1))

    mercados_full = sorted(mercados_goles + mercados_extra + [ganador_local, ganador_visitante, doble_local, doble_visitante], key=lambda x: x[2], reverse=True)
    favorito = local_name if p_local > p_empate and p_local > p_visitante else visitante_name if p_visitante > p_empate and p_visitante > p_local else "Empate"
    score, nivel, color = confianza_general(p_local, p_empate, p_visitante, mercados_full, xg_l, xg_v)

    return {
        "local": local_name, "visitante": visitante_name, "data_local": data_local, "data_visitante": data_visitante,
        "fuente": fuente, "xg_l": xg_l, "xg_v": xg_v,
        "p_local": p_local, "p_empate": p_empate, "p_visitante": p_visitante,
        "favorito": favorito, "confianza_score": score, "confianza_nivel": nivel, "confianza_color": color,
        "mercados": mercados_full, "marcadores": marcadores,
        "corners_total": corners_total, "tarjetas_total": tarjetas_total, "faltas_total": faltas_total,
        "indice_local": indice_drd(data_local, xg_l), "indice_visitante": indice_drd(data_visitante, xg_v),
    }

def lectura_final(r):
    mejor = r["mercados"][0]
    fuente_raw = str(r.get("fuente", ""))
    if "estim" in fuente_raw.lower():
        fuente_txt = "fixture real de API-Football + estimación DRD por falta de historial completo"
    elif fuente_raw.upper().startswith("API"):
        fuente_txt = "datos recientes de API-Football procesados por DRD"
    else:
        fuente_txt = "modo demo/local porque la API no cubrió ese partido o faltan estadísticas recientes"
    consejo = "Partido con lectura clara; aun así usa stake bajo." if r["confianza_score"] >= 75 else "Lectura útil pero no regalada; mejor mercado conservador." if r["confianza_score"] >= 60 else "Partido peligroso; mejor pasar si la calidad de datos no acompaña."
    return f"""
**{r['local']} vs {r['visitante']}**

Fuente: **{fuente_txt}**.  
Favorito DRD: **{r['favorito']}**.  
Marcador más probable: **{r['marcadores'][0][0]}**.  
xG modelo: **{r['local']} {r['xg_l']} - {r['xg_v']} {r['visitante']}**.  
Mercado con mejor lectura del modelo: **{mejor[1]}** ({mejor[2]}/100).

**Lectura:** {consejo}
"""
