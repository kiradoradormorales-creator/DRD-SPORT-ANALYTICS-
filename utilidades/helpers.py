def forma_visual(forma):
    mapa = {"G":"🟢G", "E":"🟡E", "P":"🔴P", "W":"🟢G", "D":"🟡E", "L":"🔴P"}
    return " ".join(mapa.get(x, x) for x in forma[-10:])

def estrellas(prob):
    if prob >= 85: return "⭐⭐⭐⭐⭐"
    if prob >= 75: return "⭐⭐⭐⭐"
    if prob >= 65: return "⭐⭐⭐"
    if prob >= 55: return "⭐⭐"
    return "⭐"

def riesgo_mercado(prob):
    if prob >= 80: return "🟢 Bajo"
    if prob >= 65: return "🟡 Medio"
    return "🔴 Alto"
