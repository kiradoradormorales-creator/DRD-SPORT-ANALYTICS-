import streamlit as st
import pandas as pd
from scipy.stats import poisson
from traductor import traducir_equipo

st.set_page_config(page_title="Apuestas DRD", page_icon="⚽", layout="wide")

st.markdown("""
<style>
.big-card {
    padding: 18px;
    border-radius: 15px;
    background-color: #111827;
    border: 1px solid #374151;
    margin-bottom: 12px;
}
.green-card {
    padding: 18px;
    border-radius: 15px;
    background-color: #064e3b;
    border: 1px solid #10b981;
    margin-bottom: 12px;
}
.yellow-card {
    padding: 18px;
    border-radius: 15px;
    background-color: #78350f;
    border: 1px solid #f59e0b;
    margin-bottom: 12px;
}
.red-card {
    padding: 18px;
    border-radius: 15px;
    background-color: #7f1d1d;
    border: 1px solid #ef4444;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

banderas = {
    "croatia": "🇭🇷",
    "panama": "🇵🇦",
    "england": "🏴",
    "ghana": "🇬🇭",
    "argentina": "🇦🇷",
    "brazil": "🇧🇷",
    "mexico": "🇲🇽",
    "spain": "🇪🇸",
    "france": "🇫🇷",
    "germany": "🇩🇪",
    "portugal": "🇵🇹",
    "colombia": "🇨🇴",
    "united states": "🇺🇸",
    "japan": "🇯🇵",
    "south korea": "🇰🇷",
    "morocco": "🇲🇦",
    "algeria": "🇩🇿",
    "senegal": "🇸🇳",
    "norway": "🇳🇴",
    "jordan": "🇯🇴",
    "qatar": "🇶🇦",
}

def bandera(equipo):
    return banderas.get(equipo, "⚽")

st.title("⚽ DRD SPORT ANALYTICS")
st.caption("Datos reales + Poisson + mercados + lectura DRD")

@st.cache_data
def cargar_datos():
    url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
    datos = pd.read_csv(url)
    datos["home_team"] = datos["home_team"].str.strip().str.lower()
    datos["away_team"] = datos["away_team"].str.strip().str.lower()
    datos["home_score"] = pd.to_numeric(datos["home_score"], errors="coerce")
    datos["away_score"] = pd.to_numeric(datos["away_score"], errors="coerce")
    return datos.dropna(subset=["home_score", "away_score"])

def estrellas(prob):
    if prob >= 80:
        return "⭐⭐⭐⭐⭐"
    elif prob >= 70:
        return "⭐⭐⭐⭐"
    elif prob >= 60:
        return "⭐⭐⭐"
    elif prob >= 50:
        return "⭐⭐"
    else:
        return "⭐"

def calcular_estadisticas(equipo, partidos):
    gf = 0
    gc = 0

    for _, p in partidos.iterrows():
        if p["home_team"] == equipo:
            gf += p["home_score"]
            gc += p["away_score"]
        else:
            gf += p["away_score"]
            gc += p["home_score"]

    return gf, gc, gf / len(partidos), gc / len(partidos)

def forma_reciente(equipo, partidos):
    forma = []

    for _, p in partidos.iterrows():
        if p["home_team"] == equipo:
            gf = p["home_score"]
            gc = p["away_score"]
        else:
            gf = p["away_score"]
            gc = p["home_score"]

        if gf > gc:
            forma.append("🟢")
        elif gf == gc:
            forma.append("🟡")
        else:
            forma.append("🔴")

    return "".join(forma)

def tarjeta_mercado(nombre, prob):
    if prob >= 75:
        tipo = "green-card"
    elif prob >= 60:
        tipo = "yellow-card"
    else:
        tipo = "red-card"

    st.markdown(
        f"""
        <div class="{tipo}">
            <h3>{nombre}</h3>
            <h2>{round(prob, 1)}%</h2>
            <p>{estrellas(prob)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

colA, colB = st.columns(2)

with colA:
    equipo_local_txt = st.text_input("Equipo local", placeholder="Ej: croacia")

with colB:
    equipo_visitante_txt = st.text_input("Equipo visitante", placeholder="Ej: panama")

if st.button("ANALIZAR PARTIDO", use_container_width=True):
    datos = cargar_datos()

    equipo1 = traducir_equipo(equipo_local_txt)
    equipo2 = traducir_equipo(equipo_visitante_txt)

    partidos1 = datos[(datos["home_team"] == equipo1) | (datos["away_team"] == equipo1)]
    partidos2 = datos[(datos["home_team"] == equipo2) | (datos["away_team"] == equipo2)]

    ultimos1 = partidos1.tail(10)
    ultimos2 = partidos2.tail(10)

    if len(ultimos1) == 0 or len(ultimos2) == 0:
        st.error("No se encontraron suficientes partidos para uno de los equipos.")
    else:
        gf1, gc1, prom1, contra1 = calcular_estadisticas(equipo1, ultimos1)
        gf2, gc2, prom2, contra2 = calcular_estadisticas(equipo2, ultimos2)

        goles_esp1 = round((prom1 + contra2) / 2, 2)
        goles_esp2 = round((prom2 + contra1) / 2, 2)

        resultados = []
        gana1 = empate = gana2 = 0
        over15 = over25 = over35 = 0
        under25 = under35 = under45 = 0
        ambos = no_ambos = 0

        for g1 in range(8):
            for g2 in range(8):
                prob = poisson.pmf(g1, goles_esp1) * poisson.pmf(g2, goles_esp2) * 100
                resultados.append((prob, f"{g1}-{g2}"))

                if g1 > g2:
                    gana1 += prob
                elif g1 == g2:
                    empate += prob
                else:
                    gana2 += prob

                total = g1 + g2

                if total > 1:
                    over15 += prob
                if total > 2:
                    over25 += prob
                if total > 3:
                    over35 += prob
                if total < 3:
                    under25 += prob
                if total < 4:
                    under35 += prob
                if total < 5:
                    under45 += prob
                if g1 > 0 and g2 > 0:
                    ambos += prob
                else:
                    no_ambos += prob

        resultados.sort(reverse=True)

        if gana1 > gana2:
            favorito = equipo1
            doble = gana1 + empate
        else:
            favorito = equipo2
            doble = gana2 + empate

        mercados = [
            ("Over 1.5 goles", over15),
            ("Over 2.5 goles", over25),
            ("Over 3.5 goles", over35),
            ("Under 2.5 goles", under25),
            ("Under 3.5 goles", under35),
            ("Under 4.5 goles", under45),
            ("Ambos anotan", ambos),
            ("No ambos anotan", no_ambos),
            (f"Doble oportunidad {favorito}/empate", doble),
            (f"Gana {favorito}", max(gana1, gana2)),
        ]

        mercados.sort(key=lambda x: x[1], reverse=True)

        st.markdown(
            f"""
            <div class="big-card">
                <h1>{bandera(equipo1)} {equipo1.upper()} vs {bandera(equipo2)} {equipo2.upper()}</h1>
                <h3>🏆 Favorito: {bandera(favorito)} {favorito.upper()}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.header("📊 Probabilidades 1X2")

        st.write(f"{bandera(equipo1)} **{equipo1.upper()} gana:** {round(gana1, 1)}%")
        st.progress(gana1 / 100)

        st.write(f"🤝 **Empate:** {round(empate, 1)}%")
        st.progress(empate / 100)

        st.write(f"{bandera(equipo2)} **{equipo2.upper()} gana:** {round(gana2, 1)}%")
        st.progress(gana2 / 100)

        st.header("📈 Estadísticas últimos 10 partidos")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"{bandera(equipo1)} {equipo1.upper()}")
            st.metric("Goles anotados", int(gf1))
            st.metric("Goles recibidos", int(gc1))
            st.metric("Promedio GF", round(prom1, 2))
            st.metric("Promedio GC", round(contra1, 2))

        with col2:
            st.subheader(f"{bandera(equipo2)} {equipo2.upper()}")
            st.metric("Goles anotados", int(gf2))
            st.metric("Goles recibidos", int(gc2))
            st.metric("Promedio GF", round(prom2, 2))
            st.metric("Promedio GC", round(contra2, 2))

        st.header("📈 Forma últimos 10 partidos")

        col5, col6 = st.columns(2)

        with col5:
            st.subheader(f"{bandera(equipo1)} {equipo1.upper()}")
            st.write(forma_reciente(equipo1, ultimos1))

        with col6:
            st.subheader(f"{bandera(equipo2)} {equipo2.upper()}")
            st.write(forma_reciente(equipo2, ultimos2))

        st.header("🔮 Goles esperados")

        col3, col4 = st.columns(2)
        col3.metric(f"{bandera(equipo1)} {equipo1.upper()}", goles_esp1)
        col4.metric(f"{bandera(equipo2)} {equipo2.upper()}", goles_esp2)

        st.header("🔥 Top 3 apuestas DRD")

        for nombre, prob in mercados[:3]:
            tarjeta_mercado(nombre, prob)

        st.header("📋 Mercados completos")

        tabla_mercados = []
        for nombre, prob in mercados:
            tabla_mercados.append({
                "Mercado": nombre,
                "Probabilidad": f"{round(prob, 1)}%",
                "Confianza": estrellas(prob)
            })

        st.dataframe(pd.DataFrame(tabla_mercados), use_container_width=True)

        st.header("🎯 Marcadores más probables")

        podio = ["🥇", "🥈", "🥉", "🏅", "🏅"]

        for i, (prob, marcador) in enumerate(resultados[:5]):
            st.markdown(f"### {podio[i]} {marcador} → {round(prob, 2)}%")

        st.header("🧠 Lectura final DRD")

        st.info(
            f"{bandera(equipo1)} {equipo1.upper()} viene con {int(gf1)} goles anotados "
            f"y {int(gc1)} recibidos en sus últimos 10 partidos. "
            f"{bandera(equipo2)} {equipo2.upper()} viene con {int(gf2)} goles anotados "
            f"y {int(gc2)} recibidos. "
            f"El favorito del modelo es {bandera(favorito)} {favorito.upper()}. "
            f"La mejor jugada detectada es {mercados[0][0]} con "
            f"{round(mercados[0][1], 1)}% de confianza."
        )