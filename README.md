# DRD SPORT ANALYTICS v1.4.0 Streamlit Ultra

Base oficial visual para subir a GitHub.

## Qué trae

- Diseño Streamlit exprimido al máximo: hero pro, tarjetas premium, ranking visual, DRD Score y mejor responsividad.
- API-Football conectada mediante `.env` o key global guardada.
- Ranking DRD con interés del modelo + respaldo final.
- Calidad del análisis y lenguaje público limpio.
- Panel admin oculto con `DRD_ADMIN_MODE=1`.

## Cómo correr

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Configuración

Crea un archivo `.env` junto a `app.py`:

```env
API_FOOTBALL_KEY=tu_key
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
CACHE_TTL_SECONDS=900
TEMPORADA_DEFAULT=2025
```

No subas tu `.env` a GitHub.
