traducciones = {
    "inglaterra": "england",
    "ghana": "ghana",
    "croacia": "croatia",
    "panama": "panama",
    "panamá": "panama",
    "mexico": "mexico",
    "méxico": "mexico",
    "argentina": "argentina",
    "brasil": "brazil",
    "francia": "france",
    "alemania": "germany",
    "españa": "spain",
    "espana": "spain",
    "portugal": "portugal",
    "colombia": "colombia",
    "eeuu": "united states",
    "usa": "united states",
    "estados unidos": "united states",
    "japon": "japan",
    "japón": "japan",
    "corea": "south korea",
    "corea del sur": "south korea",
    "marruecos": "morocco",
    "argelia": "algeria",
    "senegal": "senegal",
    "noruega": "norway",
    "jordania": "jordan",
    "qatar": "qatar",
    "croatia": "croatia",
    "england": "england"
}

def traducir_equipo(nombre):
    nombre = nombre.strip().lower()
    return traducciones.get(nombre, nombre)