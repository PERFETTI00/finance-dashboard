# Finance Dashboard (Streamlit + yfinance)

Un panel moderno para analizar precios, ratios y estados financieros de empresas públicas
utilizando datos de Yahoo Finance a través de `yfinance`.

## 🚀 Características
- Ticker principal + comparativa con pares
- Gráficos interactivos de precio y distribución de retornos (Plotly)
- Ratios clave (P/E, P/S, Current Ratio, ROE, ROA)
- Visualización de estados financieros (Income, Balance, Cash Flow)
- Tema oscuro moderno y métricas en tarjetas
- Descarga de datos y gráficos (CSV/PNG) y **watchlist** persistente
- Caché para acelerar descargas y cálculos

## 🧱 Estructura
```
finance-dashboard/
├─ app.py
├─ requirements.txt
├─ environment.yml
├─ .streamlit/
│  └─ config.toml
└─ src/
   ├─ finance.py
   ├─ ui.py
   └─ watchlist.py
```

## 🐍 Entorno con Conda
```bash
conda env create -f environment.yml
conda activate finance-dashboard
```

## ▶️ Ejecutar
```bash
streamlit run app.py
```

## 💡 Notas
- Para exportar gráficos a PNG, se usa `kaleido`.
- Si ya tienes un entorno creado, puedes instalar con:
  `conda install -c conda-forge streamlit yfinance pandas numpy plotly python-dateutil requests pytz kaleido`