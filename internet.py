import pandas as pd
from scipy.stats import poisson
from traductor import traducir_equipo

url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

print("⬇ Descargando base...")
datos = pd.read_csv(url)
print("✅ Base descargada")

datos["home_team"] = datos["home_team"].str.strip().str.lower()
datos["away_team"] = datos["away_team"].str.strip().str.lower()
datos["home_score"] = pd.to_numeric(datos["home_score"], errors="coerce")
datos["away_score"] = pd.to_numeric(datos["away_score"], errors="coerce")
datos = datos.dropna(subset=["home_score", "away_score"])

equipo1 = traducir_equipo(input("Equipo local: "))
equipo2 = traducir_equipo(input("Equipo visitante: "))

partidos1 = datos[(datos["home_team"] == equipo1) | (datos["away_team"] == equipo1)]
partidos2 = datos[(datos["home_team"] == equipo2) | (datos["away_team"] == equipo2)]

ultimos1 = partidos1.tail(10)
ultimos2 = partidos2.tail(10)

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

if len(ultimos1) > 0 and len(ultimos2) > 0:
    gf1, gc1, prom1, contra1 = calcular_estadisticas(equipo1, ultimos1)
    gf2, gc2, prom2, contra2 = calcular_estadisticas(equipo2, ultimos2)

    goles_esp1 = round((prom1 + contra2) / 2, 2)
    goles_esp2 = round((prom2 + contra1) / 2, 2)

    resultados = []
    gana1 = empate = gana2 = 0
    over15 = over25 = under45 = ambos = no_ambos = 0

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
        ("Under 4.5 goles", under45),
        ("Ambos anotan", ambos),
        ("No ambos anotan", no_ambos),
        (f"Doble oportunidad {favorito}/empate", doble),
        (f"Gana {favorito}", max(gana1, gana2)),
    ]

    mercados.sort(key=lambda x: x[1], reverse=True)

    print()
    print("📖 HISTORIAL")
    print(equipo1, ":", len(partidos1), "partidos")
    print(equipo2, ":", len(partidos2), "partidos")

    print()
    print("📊 ESTADÍSTICAS ÚLTIMOS 10 PARTIDOS")
    print()
    print(equipo1)
    print("Goles anotados:", gf1)
    print("Goles recibidos:", gc1)
    print("Promedio anotados:", round(prom1, 2))
    print("Promedio recibidos:", round(contra1, 2))

    print()
    print(equipo2)
    print("Goles anotados:", gf2)
    print("Goles recibidos:", gc2)
    print("Promedio anotados:", round(prom2, 2))
    print("Promedio recibidos:", round(contra2, 2))

    print()
    print("🔮 GOLES ESPERADOS")
    print(equipo1, ":", goles_esp1)
    print(equipo2, ":", goles_esp2)

    print()
    print("📈 PROBABILIDADES 1X2")
    print(equipo1, "gana:", round(gana1, 1), "%", estrellas(gana1))
    print("Empate:", round(empate, 1), "%", estrellas(empate))
    print(equipo2, "gana:", round(gana2, 1), "%", estrellas(gana2))

    print()
    print("🏆 FAVORITO:", favorito)

    print()
    print("🔥 MERCADOS")
    for nombre, prob in mercados:
        print(nombre, "->", round(prob, 1), "%", estrellas(prob))

    print()
    print("🎯 TOP 3 APUESTAS DRD")
    for nombre, prob in mercados[:3]:
        print(nombre, "->", round(prob, 1), "%", estrellas(prob))

    print()
    print("🏆 MARCADORES MÁS PROBABLES")
    for prob, marcador in resultados[:5]:
        print(marcador, "->", round(prob, 2), "%")

    print()
    print("🧠 LECTURA FINAL DRD")
    print(f"{equipo1} viene con {gf1} goles anotados y {gc1} recibidos en sus últimos 10.")
    print(f"{equipo2} viene con {gf2} goles anotados y {gc2} recibidos en sus últimos 10.")
    print("Mejor jugada:", mercados[0][0])
    print("Confianza:", round(mercados[0][1], 1), "%", estrellas(mercados[0][1]))

else:
    print("❌ No se encontraron suficientes partidos para uno de los equipos.")