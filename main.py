from scipy.stats import poisson

print("🔥 APUESTAS DRD 🔥")
print()

equipo1 = input("Equipo local: ").lower()
equipo2 = input("Equipo visitante: ").lower()

equipos = {
    "inglaterra": 2.1,
    "ghana": 1.1,
    "argentina": 2.4,
    "brasil": 2.3,
    "mexico": 1.6,
    "panama": 1.0,
    "francia": 2.5,
    "españa": 2.2,
    "alemania": 2.1,
    "portugal": 2.0
}

def estrellas(prob):
    if prob >= 80:
        return "⭐⭐⭐⭐"
    elif prob >= 70:
        return "⭐⭐⭐"
    elif prob >= 60:
        return "⭐⭐"
    else:
        return "⭐"

if equipo1 in equipos and equipo2 in equipos:
    ataque1 = equipos[equipo1]
    ataque2 = equipos[equipo2]

    resultados = []
    gana1 = empate = gana2 = 0
    over15 = over25 = over35 = 0
    under25 = under35 = under45 = 0
    ambos = no_ambos = 0

    for g1 in range(8):
        for g2 in range(8):
            prob = poisson.pmf(g1, ataque1) * poisson.pmf(g2, ataque2) * 100
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
        gana_favorito = gana1
    else:
        favorito = equipo2
        doble = gana2 + empate
        gana_favorito = gana2

    mercados = [
        (f"Doble oportunidad {favorito}/empate", doble),
        (f"Gana {favorito}", gana_favorito),
        ("Over 1.5 goles", over15),
        ("Over 2.5 goles", over25),
        ("Over 3.5 goles", over35),
        ("Under 2.5 goles", under25),
        ("Under 3.5 goles", under35),
        ("Under 4.5 goles", under45),
        ("Ambos anotan", ambos),
        ("No ambos anotan", no_ambos)
    ]

    mercados.sort(key=lambda x: x[1], reverse=True)

    print()
    print("⚽ Partido:")
    print(equipo1, "vs", equipo2)

    print()
    print("📊 1X2:")
    print(equipo1, "gana:", round(gana1, 1), "%")
    print("empate:", round(empate, 1), "%")
    print(equipo2, "gana:", round(gana2, 1), "%")

    print()
    print("🏆 Favorito:", favorito)

    print()
    print("🔥 TOP 3 MERCADOS DRD:")
    for nombre, prob in mercados[:3]:
        print(nombre, "->", round(prob, 1), "%", estrellas(prob))

    print()
    print("⚽ Marcadores más probables:")
    for prob, marcador in resultados[:5]:
        print(marcador, "->", round(prob, 2), "%")

    print()
    print("💰 Lectura final:")
    mejor, prob_mejor = mercados[0]

    if prob_mejor >= 80:
        print("🟢 Mejor jugada:", mejor)
        print("Confianza alta:", round(prob_mejor, 1), "%")
    elif prob_mejor >= 70:
        print("🟡 Jugada aceptable:", mejor)
        print("Confianza media:", round(prob_mejor, 1), "%")
    else:
        print("🔴 Partido peligroso. Mejor no meterle fuerte.")

else:
    print("❌ Equipo no registrado.")
    print("Equipos disponibles:")
    print(list(equipos.keys()))