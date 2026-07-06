from __future__ import annotations

import pandas as pd
import streamlit as st

from config import APP_NAME, APP_VERSION, API_FOOTBALL_KEY, masked_key, save_api_key, admin_mode_enabled
from modelos.indice_drd import nivel_indice
from modelos.motor_drd import analizar_partido, lectura_final
from servicios.data_service import (
    estado_fuente,
    partidos_disponibles,
    partidos_demo,
    get_match_teams,
    obtener_stats_api_o_demo,
    pretty_team_name,
    team_label,
    match_label,
    ultimo_error_api,
    ultima_meta_api,
    filtrar_matches,
)
from servicios.quality_service import evaluar_calidad_analisis
from ui.styles import CSS
from utilidades.helpers import forma_visual, estrellas, riesgo_mercado


st.set_page_config(page_title=APP_NAME, page_icon="⚽", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

IS_ADMIN = admin_mode_enabled()

st.markdown(
    f"""
    <div class='drd-hero-pro'>
      <div class='drd-hero-glow'></div>
      <div class='drd-hero-left'>
        <div class='drd-kicker'>DRD LAB · análisis deportivo transparente</div>
        <div class='drd-title-pro'>⚽ {APP_NAME}</div>
        <div class='drd-sub-pro'>{APP_VERSION} · Ranking DRD, calidad del análisis y riesgo visible en una sola lectura. Datos claros, sin prometer resultados.</div>
        <div class='drd-hero-badges'>
          <span class='badge badge-blue'>📊 Datos claros</span>
          <span class='badge badge-green'>🎯 Ranking DRD</span>
          <span class='badge badge-yellow'>⚠️ Riesgo visible</span>
          <span class='badge badge-purple'>🧠 Lectura explicada</span>
        </div>
      </div>
      <div class='drd-hero-right'>
        <div class='drd-score-orb'>
          <div class='drd-score-num'>DRD</div>
          <div class='drd-score-label'>SCORE</div>
        </div>
        <div class='drd-mini-feed'>
          <div class='feed-row'><span>🥇</span><b>Ranking</b><em>oportunidades</em></div>
          <div class='feed-row'><span>🧪</span><b>Calidad</b><em>datos usados</em></div>
          <div class='feed-row'><span>🛡️</span><b>Riesgo</b><em>lectura honesta</em></div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

status = estado_fuente()

with st.sidebar:
    st.header("⚽ DRD")
    if status["ok"]:
        raw = status.get("raw", {}) or {}
        account = raw.get("account", {}) if isinstance(raw, dict) else {}
        requests_info = raw.get("requests", {}) if isinstance(raw, dict) else {}
        plan = account.get("plan", "Free") or "Free"
        used = requests_info.get("current", "?")
        limit = requests_info.get("limit_day", "?")
        st.markdown(
            f"""
            <div class='drd-status-ok'>
                🟢 Fuente activa<br>
                <span style='opacity:.86'>Plan {plan}</span><br>
                <span style='opacity:.86'>Uso diario: {used}/{limit}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div class='drd-status-warn'>🟡 Fuente limitada<br><span style='opacity:.86'>DRD mantiene modo demo.</span></div>""",
            unsafe_allow_html=True,
        )

    days = st.slider("Ventana de partidos", 1, 14, 7)
    st.markdown("---")
    st.caption("DRD ordena oportunidades y muestra el nivel de respaldo. No garantiza resultados.")
    if IS_ADMIN:
        st.markdown("---")
        st.caption("🔒 Modo administrador activo.")


def load_matches(days: int):
    api_matches = partidos_disponibles(days=days)
    if api_matches:
        return api_matches, "DATOS"
    return partidos_demo(), "DEMO"


def quality_badge(quality: dict) -> str:
    if quality["verified"]:
        return "<span class='verified'>🟢 DRD VERIFIED</span>"
    if quality["score"] >= 60:
        return "<span class='badge badge-yellow'>🟡 Lectura útil</span>"
    if quality["score"] >= 40:
        return "<span class='badge badge-yellow'>🟠 Lectura exploratoria</span>"
    return "<span class='badge badge-red'>🔴 Datos insuficientes</span>"



def score_tone(score: int) -> str:
    if score >= 85:
        return "green"
    if score >= 65:
        return "yellow"
    if score >= 45:
        return "orange"
    return "red"


def render_score_orb(label: str, score: int, subtitle: str = ""):
    tone = score_tone(int(score))
    st.markdown(
        f"""
        <div class='score-orb-card score-{tone}' style='--score:{max(0,min(100,int(score)))};'>
          <div class='score-ring'><div><span>{int(score)}</span><small>/100</small></div></div>
          <div class='score-meta'><b>{label}</b><p>{subtitle}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(title: str, value: str, subtitle: str, icon: str = "⚽", tone: str = "blue"):
    st.markdown(
        f"""
        <div class='kpi-card kpi-{tone}'>
          <div class='kpi-icon'>{icon}</div>
          <div class='kpi-title'>{title}</div>
          <div class='kpi-value'>{value}</div>
          <div class='kpi-sub'>{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rank_html(idx: int, mercado: str, categoria: str, prob: int | float, score_final: int, etiqueta: str, aviso: str):
    medalla = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "▫️"
    tone = score_tone(score_final)
    st.markdown(
        f"""
        <div class='rank-card-pro rank-{tone}'>
          <div class='rank-left'>
            <div class='rank-medal'>{medalla}</div>
            <div>
              <div class='rank-title-pro'>{mercado}</div>
              <div class='rank-sub-pro'>{categoria} · {etiqueta}</div>
              <div class='rank-note'>{aviso}</div>
            </div>
          </div>
          <div class='rank-scores'>
            <div class='rank-score-box'><span>{prob}</span><small>Interés DRD</small></div>
            <div class='rank-score-box main'><span>{score_final}</span><small>Respaldo final</small></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_quality_public(quality: dict):
    st.markdown("<div class='drd-section-title'>🧪 Calidad del análisis</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.3, 1.1, 2.1])
    with c1:
        render_score_orb("Calidad de datos", quality["score"], quality["nivel"])
    with c2:
        render_kpi_card("Estado", quality["public_status"], "Nivel de lectura", "🛡️", score_tone(quality["score"]))
    with c3:
        st.markdown(quality_badge(quality), unsafe_allow_html=True)
        st.caption(quality["user_action"])

    if quality["score"] < 60:
        st.warning(quality["mensaje"])
    elif quality["verified"]:
        st.success(quality["mensaje"])
    else:
        st.info(quality["mensaje"])

    with st.expander("Ver información disponible", expanded=True):
        a, b = st.columns(2)
        with a:
            st.subheader("✅ Información disponible")
            if quality["available"]:
                for item in quality["available"]:
                    st.write(f"✅ {item['nombre']}")
            else:
                st.write("Aún no hay información suficiente.")
        with b:
            st.subheader("⚠️ Información faltante")
            if quality["missing"]:
                for item in quality["missing"]:
                    st.write(f"⚠️ {item['nombre']}")
            else:
                st.write("No se detectaron faltantes importantes.")


def render_public_method(quality: dict):
    st.markdown("<div class='drd-section-title'>📊 Información usada por DRD</div>", unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        st.markdown("<div class='card'><h2>📌 Datos del partido</h2><p>Información confirmada o disponible para este encuentro.</p></div>", unsafe_allow_html=True)
        for item in quality["available"][:6]:
            st.write(f"✅ {item['nombre']}")
        if len(quality["available"]) > 6:
            st.caption(f"+ {len(quality['available']) - 6} datos disponibles más.")
    with b:
        st.markdown("<div class='card'><h2>🧠 Lectura DRD</h2><p>Interpretación calculada por el modelo, no un hecho garantizado.</p></div>", unsafe_allow_html=True)
        componentes = [x for x in quality["model_components"] if x["ok"]]
        for item in componentes:
            st.write(f"✅ {item['nombre']}")
        if quality["estimated"]:
            st.warning("Parte de esta lectura usa estimación porque faltan estadísticas completas.")


def render_admin_quality(quality: dict, fuente: str):
    with st.expander("🔒 Detalle técnico admin", expanded=False):
        checks_df = pd.DataFrame(
            [
                {
                    "Dato técnico": x["nombre"],
                    "Estado": "Disponible" if x["ok"] else "Falta",
                    "Tipo": "Proveedor" if x["tipo"] == "oficial" else "Modelo DRD",
                }
                for x in quality["checks"]
            ]
        )
        st.dataframe(checks_df, use_container_width=True, hide_index=True)
        st.caption(f"Fuente interna: {fuente}")


def render_partidos_table(matches: list[dict]):
    rows = []
    for m in matches[:300]:
        h, a = get_match_teams(m)
        league = m.get("league", m.get("competition", {}))
        rows.append(
            {
                "Local": pretty_team_name(h.get("name", "")),
                "Visitante": pretty_team_name(a.get("name", "")),
                "Torneo": league.get("name", ""),
                "País": league.get("country", ""),
                "Fecha": (m.get("fixture", {}).get("date") or m.get("utcDate", ""))[:16],
                "Estado": m.get("fixture", {}).get("status", {}).get("short", ""),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_admin_config():
    st.header("🔒 Administración")
    st.info("Este panel es solo para ti. No debe estar activo en la versión pública.")
    if API_FOOTBALL_KEY:
        st.success(f"API key detectada: {masked_key()}")
    else:
        st.warning("No hay API key guardada. La app seguirá en modo demo hasta que la guardes.")
    nueva_key = st.text_input("API_FOOTBALL_KEY", type="password", placeholder="Pega aquí tu key")
    guardar_global = st.checkbox("Guardar para futuras versiones de DRD en esta PC", value=True)
    if st.button("Guardar API Key", type="primary"):
        try:
            ruta = save_api_key(nueva_key, save_global=guardar_global)
            st.success(f"Key guardada correctamente en: {ruta}")
            st.info("Reinicia la app con Ctrl+C y vuelve a correr: python -m streamlit run app.py")
        except Exception as e:
            st.error(f"No pude guardar la key: {e}")

    st.markdown("---")
    st.subheader("Estado técnico")
    st.json(status)


public_tabs = ["🏠 Inicio", "🎯 Analizador", "📅 Partidos", "🤖 IA DRD", "💎 Premium"]
if IS_ADMIN:
    public_tabs.append("🔒 Admin")

tabs = st.tabs(public_tabs)
tab1, tab2, tab3, tab4, tab5 = tabs[:5]
tab_admin = tabs[5] if IS_ADMIN else None

with tab1:
    st.markdown("<div class='drd-section-title'>🏠 Centro DRD</div>", unsafe_allow_html=True)
    st.markdown("<div class='drd-section-sub'>Una página de análisis debe ayudarte a entender el partido, no venderte humo.</div>", unsafe_allow_html=True)
    st.write("")

    c1, c2, c3 = st.columns([1.2, 1, 1])
    c1.markdown("""
    <div class='drd-card'>
      <h2>🎯 Ranking DRD</h2>
      <p>Ordena mercados por interés del modelo y respaldo de información. Ideal para comparar oportunidades sin tratar cada lectura como certeza.</p>
    </div>
    """, unsafe_allow_html=True)
    c2.markdown("""
    <div class='drd-card'>
      <h2>🧪 Calidad</h2>
      <p>DRD avisa si el partido tiene datos fuertes, parciales o exploratorios antes de mostrar el ranking.</p>
    </div>
    """, unsafe_allow_html=True)
    c3.markdown("""
    <div class='drd-card'>
      <h2>⚠️ Riesgo</h2>
      <p>Cada lectura muestra si es fuerte, moderada o ligera. Sin prometer resultados.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='drd-section-title'>🔥 Flujo de análisis</div>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    f1.markdown("<div class='drd-card-compact'><b>1. Elige partido</b><br><span class='small-muted'>Busca por equipo o torneo.</span></div>", unsafe_allow_html=True)
    f2.markdown("<div class='drd-card-compact'><b>2. DRD mide calidad</b><br><span class='small-muted'>Detecta información disponible.</span></div>", unsafe_allow_html=True)
    f3.markdown("<div class='drd-card-compact'><b>3. Ordena mercados</b><br><span class='small-muted'>Interés del modelo + respaldo.</span></div>", unsafe_allow_html=True)
    f4.markdown("<div class='drd-card-compact'><b>4. Decide con contexto</b><br><span class='small-muted'>Tú decides, DRD no promete.</span></div>", unsafe_allow_html=True)

    st.markdown("<div class='drd-section-title'>📌 Estados de lectura</div>", unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.markdown("<div class='drd-card'><h2>🟢 Fuerte</h2><p>Datos amplios y lectura con buen respaldo. Puede aparecer como DRD Verified.</p></div>", unsafe_allow_html=True)
    b.markdown("<div class='drd-card'><h2>🟡 Útil</h2><p>Hay datos suficientes para comparar, pero faltan algunas capas de información.</p></div>", unsafe_allow_html=True)
    c.markdown("<div class='drd-card'><h2>🟠 Exploratoria</h2><p>El modelo puede sugerir tendencias, pero no debe tratarse como jugada principal.</p></div>", unsafe_allow_html=True)

with tab2:
    matches, modo = load_matches(days)
    st.markdown("### 🔎 Selecciona un partido")
    st.caption(f"Modo actual: **{'Datos reales disponibles' if modo == 'DATOS' else 'Demo'}**")

    if modo == "DATOS":
        meta = ultima_meta_api()
        st.success(f"Partidos cargados: {len(matches)} · ventana {meta.get('from','')} → {meta.get('to','')}")
        if meta.get("auto_window"):
            st.info("El plan gratuito limita fechas. DRD ajustó la ventana automáticamente para mostrar partidos disponibles.")
    else:
        err = ultimo_error_api()
        st.warning("No se cargaron partidos reales. DRD mantiene modo demo para que puedas revisar la interfaz.")
        if IS_ADMIN and err:
            st.caption(f"Detalle admin: {err}")

    filtro = st.text_input("Buscar equipo o torneo", placeholder="Ej. mundial, world cup, México, Champions, Liga MX...")
    if filtro:
        filtrados = filtrar_matches(matches, filtro)
        if filtrados:
            matches = filtrados
            st.success(f"Filtro aplicado: {len(matches)} partidos encontrados.")
        else:
            st.warning("No encontré partidos con ese filtro. Prueba con el nombre del torneo o equipo en inglés.")

    if not matches:
        st.error("No hay partidos para mostrar.")
        st.stop()

    options = [match_label(m) for m in matches]
    selected = st.selectbox("Partido", options)
    match = matches[options.index(selected)]
    home, away = get_match_teams(match)
    local_name = pretty_team_name(home.get("name", "Local"))
    visitante_name = pretty_team_name(away.get("name", "Visitante"))

    c1, c2, c3 = st.columns([2, .75, 2])
    with c1:
        st.markdown(f"<div class='drd-match-card pro-home'><div class='team-tag'>LOCAL</div><h2>{team_label(home)}</h2><p>Listo para lectura DRD</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='vs-pro'><span>VS</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='drd-match-card pro-away'><div class='team-tag'>VISITANTE</div><h2>{team_label(away)}</h2><p>Comparativa activa</p></div>", unsafe_allow_html=True)

    if not st.button("ANALIZAR PARTIDO", type="primary", use_container_width=True):
        st.info("Selecciona un partido y analiza. DRD mostrará si la lectura es fuerte, parcial o insuficiente.")
        st.stop()

    data_local, data_visitante, fuente = obtener_stats_api_o_demo(home, away, match)
    if not data_local or not data_visitante:
        st.error("No hay datos suficientes para este partido.")
        st.stop()

    r = analizar_partido(local_name, visitante_name, data_local, data_visitante, fuente=fuente)
    quality = evaluar_calidad_analisis(data_local, data_visitante, fuente, match)

    st.markdown("---")
    render_quality_public(quality)
    render_public_method(quality)
    if IS_ADMIN:
        render_admin_quality(quality, fuente)

    st.markdown("---")
    st.markdown("<div class='drd-section-title'>🎯 Resumen DRD</div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns([1.2, 1.2, 1, 1])
    with k1:
        render_kpi_card("Lectura principal", r["favorito"], "Equipo con mejor lectura", "🏆", "green" if r["confianza_score"] >= 70 else "yellow")
    with k2:
        render_score_orb("Confianza DRD", r["confianza_score"], r["confianza_nivel"])
    with k3:
        render_kpi_card("Nivel", r["confianza_nivel"], "Fuerza del modelo", "📌", score_tone(r["confianza_score"]))
    with k4:
        render_kpi_card("Marcador estimado", r["marcadores"][0][0], "Escenario más probable", "🎯", "blue")

    if quality["score"] < 60:
        st.warning("DRD no recomienda usar este partido para decisiones fuertes. La lectura es exploratoria.")
    elif quality["estimated"]:
        st.warning("La lectura usa estimación porque faltan estadísticas completas. Úsala como referencia, no como certeza.")

    st.markdown("<div class='drd-section-title'>📈 Lectura 1X2</div>", unsafe_allow_html=True)
    pa, pb, pc = st.columns(3)
    with pa:
        render_kpi_card(local_name, f"{r['p_local']}%", "Lectura 1", "🏠", "blue")
        st.progress(r["p_local"] / 100)
    with pb:
        render_kpi_card("Empate", f"{r['p_empate']}%", "Lectura X", "🤝", "yellow")
        st.progress(r["p_empate"] / 100)
    with pc:
        render_kpi_card(visitante_name, f"{r['p_visitante']}%", "Lectura 2", "✈️", "purple")
        st.progress(r["p_visitante"] / 100)
    if quality["score"] < 60:
        st.caption("Lectura exploratoria: los porcentajes son una estimación del modelo DRD con respaldo limitado.")
    else:
        st.caption("Lectura del modelo DRD basada en la información disponible. No garantiza resultado.")

    st.markdown("<div class='drd-section-title'>🎯 Ranking DRD</div>", unsafe_allow_html=True)
    if quality["score"] >= 85:
        st.success("Lectura fuerte: estos mercados tienen buen respaldo de información y del modelo.")
    elif quality["score"] >= 60:
        st.info("Lectura útil: DRD muestra las mejores oportunidades, pero aún faltan algunas capas de información.")
    else:
        st.warning("Lectura exploratoria: DRD sí muestra oportunidades, pero no las considera recomendaciones fuertes.")

    st.caption("El ranking combina dos cosas: qué tanto le gusta el mercado al modelo y qué tan completa es la información disponible.")

    calidad = int(quality.get("score", 0))
    factor_respaldo = 0.55 + (0.45 * calidad / 100)

    for idx, (categoria, mercado, prob) in enumerate(r["mercados"][:6], start=1):
        score_final = int(round(prob * factor_respaldo))
        if score_final >= 80 and calidad >= 75:
            etiqueta = "🟢 Oportunidad fuerte"
            aviso = "Buen equilibrio entre modelo y datos disponibles."
        elif score_final >= 65:
            etiqueta = "🟡 Oportunidad moderada"
            aviso = "Interesante, pero conviene revisar el contexto antes de decidir."
        elif score_final >= 50:
            etiqueta = "🟠 Lectura ligera"
            aviso = "Puede servir como referencia, no como jugada principal."
        else:
            etiqueta = "🔴 Muy especulativa"
            aviso = "DRD la muestra para comparar, pero no la prioriza."

        render_rank_html(idx, mercado, categoria, prob, score_final, etiqueta, aviso)

    if quality["score"] < 60:
        st.info("Tip DRD: cuando la calidad del análisis es baja, usa el ranking para observar tendencias, no para tomar decisiones fuertes.")

    st.markdown("<div class='drd-section-title'>📌 Métricas base</div>", unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    for col, equipo, data in [(t1, local_name, r["data_local"]), (t2, visitante_name, r["data_visitante"] )]:
        with col:
            st.subheader(f"{data.get('emoji','⚽')} {equipo}")
            a, b, c = st.columns(3)
            a.metric("Goles a favor", data["gf"])
            b.metric("Goles recibidos", data["gc"])
            c.metric("Muestra", data.get("partidos_usados", 10))
            st.write("Forma:", forma_visual(data["forma"]))
            if quality["estimated"]:
                st.caption("Algunas métricas pueden ser estimaciones por falta de cobertura completa.")

    if IS_ADMIN:
        st.header("🔒 Índice técnico DRD")
        df_indice = pd.DataFrame({"Factor": list(r["indice_local"].keys()), local_name: list(r["indice_local"].values()), visitante_name: list(r["indice_visitante"].values())})
        st.dataframe(df_indice, use_container_width=True, hide_index=True)
        ci1, ci2 = st.columns(2)
        ci1.metric(f"Índice {local_name}", r["indice_local"]["Índice DRD"], nivel_indice(r["indice_local"]["Índice DRD"]))
        ci2.metric(f"Índice {visitante_name}", r["indice_visitante"]["Índice DRD"], nivel_indice(r["indice_visitante"]["Índice DRD"]))

    st.markdown("<div class='drd-section-title'>🧠 Lectura final</div>", unsafe_allow_html=True)
    st.info(lectura_final(r))

with tab3:
    st.markdown("<div class='drd-section-title'>📅 Partidos disponibles</div>", unsafe_allow_html=True)
    matches, modo = load_matches(days)
    if modo == "DATOS":
        st.success(f"Se encontraron {len(matches)} partidos en la ventana disponible.")
    else:
        st.warning("No se encontraron partidos reales para esta ventana. Mostrando demo.")
    filtro_tab = st.text_input("Filtrar tabla", placeholder="world cup, spain, méxico, liga...", key="filtro_tab_partidos")
    if filtro_tab:
        matches = filtrar_matches(matches, filtro_tab) or []
    render_partidos_table(matches)

with tab4:
    st.markdown("<div class='drd-section-title'>🤖 IA DRD</div>", unsafe_allow_html=True)
    st.info("La IA DRD explicará las lecturas cuando haya datos suficientes. Primero se califica la calidad, luego se interpreta el partido.")
    st.markdown(
        "<span class='badge'>Calidad</span><span class='badge'>Forma</span><span class='badge'>Localía</span><span class='badge'>Riesgo</span><span class='badge'>DRD Verified</span>",
        unsafe_allow_html=True,
    )

with tab5:
    st.markdown("<div class='drd-section-title'>💎 Premium futuro</div>", unsafe_allow_html=True)
    st.markdown("<div class='drd-section-sub'>DRD no se vende como bola de cristal. Se vende como una mesa de análisis clara, rápida y transparente.</div>", unsafe_allow_html=True)
    st.write("")
    p1, p2 = st.columns([1, 1.2])
    with p1:
        st.markdown("""
        <div class='drd-premium-card'>
          <span class='badge badge-blue'>Gratis</span>
          <h2>Explorar partidos</h2>
          <div class='drd-price'>$0</div>
          <div class='drd-feature'>✅ Partidos disponibles</div>
          <div class='drd-feature'>✅ Lectura básica</div>
          <div class='drd-feature'>✅ Calidad del análisis</div>
          <div class='drd-feature'>✅ Ranking limitado</div>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown("""
        <div class='drd-premium-card'>
          <span class='badge badge-green'>Premium futuro</span>
          <h2>Centro de decisión DRD</h2>
          <div class='drd-price'>$99 <span style='font-size:18px;color:#94A3B8'>MXN/mes</span></div>
          <div class='drd-feature'>🔥 Análisis ilimitados</div>
          <div class='drd-feature'>🎯 Ranking DRD completo</div>
          <div class='drd-feature'>📊 Historial y dashboard</div>
          <div class='drd-feature'>🔔 Alertas por oportunidad</div>
          <div class='drd-feature'>🧠 IA DRD explicando cada lectura</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='drd-section-title'>🚀 Próximas funciones</div>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    g1.markdown("<div class='card'><h2>📈 Dashboard</h2><p>Rachas, favoritos, historial y seguimiento de lecturas.</p></div>", unsafe_allow_html=True)
    g2.markdown("<div class='card'><h2>🔔 Alertas</h2><p>Avisos cuando DRD detecte partidos con buen respaldo.</p></div>", unsafe_allow_html=True)
    g3.markdown("<div class='card'><h2>🧠 IA DRD</h2><p>Explicaciones claras para entender por qué un mercado aparece arriba.</p></div>", unsafe_allow_html=True)

if IS_ADMIN and tab_admin is not None:
    with tab_admin:
        render_admin_config()
