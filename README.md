# 📊 Finance Dashboard

![Finance Dashboard](https://via.placeholder.com/1000x400?text=Finance+Dashboard+Preview)

## 🚀 Descripción
**Finance Dashboard** es una aplicación interactiva en **Python + Streamlit** para analizar y visualizar datos de **acciones, ETFs y criptomonedas** usando **yfinance**. Incluye indicadores técnicos, comparativas entre activos, un resumen rápido de mercado y modo claro/oscuro.

> ℹ️ **Nota**: Esta versión **no incluye ratios ni estados financieros**. Se pueden añadir más adelante como mejora.

---

## ✨ Funcionalidades

- **Selección de activos** desde un menú (y campo para escribir un ticker).
- **Precios históricos** con periodos e intervalos configurables.
- **Indicadores técnicos**:
  - SMA (Simple Moving Average)
  - EMA (Exponential Moving Average)
  - Bandas de Bollinger
  - RSI (Relative Strength Index)
- **Comparativa de activos** (multiselección).
- **Resumen de mercado** (SPY, QQQ, BTC) en la barra lateral.
- **Modo claro/oscuro** con contraste optimizado.
- **Emoji dinámico** según el ticker.
- **Descargas** de precios y comparativas (CSV/PNG).
- **Watchlist** para guardar tickers frecuentes.

---

## 🛠 Tecnologías

- Python 3.12+
- Streamlit
- yfinance
- Plotly
- Pandas
- NumPy

---

## 📦 Instalación y ejecución

### 1) Clonar el repo
```bash
git clone https://github.com/TU_USUARIO/finance-dashboard.git
cd finance-dashboard
```

### 2) Crear entorno (Conda) - Recomendado
```conda env create -f environment.yml```

### 3) O instalar con Pip
```pip install -r requirements.txt```

### 4) Eejecutar
```
streamlit run app.py
```

---

## 📂 Estructura del proyecto
```
.
├── app.py
├── src/
│   ├── finance.py
│   ├── ui.py
│   └── watchlist.py
├── requirements.txt
├── environment.yml
├── README.md
└── LICENSE
```


---

## 📸 Capturas

---

## ⚠️ Notas
- Los datos provienen de yfinance (pueden tener retraso respecto a tiempo real).
- Algunos tickers pueden no devolver toda la información.
- El resumen de mercado se actualiza al recargar la página (puedes activar auto-refresco si lo deseas).

---

## 🗺️ Roadmap (Próximas mejoras)
- Ratios y estados financieros (si están disponibles en Yahoo Finance).
- Exportación de informes en PDF.
- Despliegue en Streamlit Community Cloud.
- Logo/branding personalizado.

---

## 📄 Licencia
Este proyecto se distribuye bajo la licencia MIT.

---

Hecho por **Miguel Ángel Perfetti** www.linkedin.com/in/miguelangelperfetti
