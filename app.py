import io
import streamlit as st
import pandas as pd
import plotly.express as px
from src.finance import (
    price_history,
    annual_returns,
    rolling_volatility,
    compute_ratios,
    get_financials,
    fundamentals_available,
    technicals,
)
from src.ui import metric_card  # seguimos usando las tarjetas
from src.watchlist import load_watchlist, save_watchlist

# =========================
# Config & helpers sesión
# =========================
st.set_page_config(page_title="Finance Dashboard", page_icon="📈", layout="wide")

def sget(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

def sset(key, value):
    st.session_state[key] = value

def apply_theme(dark: bool):
    """
    Tema claro/oscuro consistente con especial énfasis en el SIDEBAR:
    - Fondo, texto, inputs, multiselect chips, selects, botones
    - Bordes y divisores
    - Dataframes con filas alternas
    """
    if dark:
        bg = "#0f1115"            # fondo app
        fg = "#e6e6e6"            # texto principal
        muted = "#a1a1aa"         # texto secundario
        card = "#111318"          # bloques/inputs
        border = "#1f2430"        # bordes
        sidebar_bg = "#0b0e14"    # fondo sidebar
        sidebar_border = "#1b2130"
        chip_bg = "#1c2230"
        chip_text = "#e6e6e6"
        placeholder = "#9aa0aa"
        alt_row = "#141821"
        accent = "#7c3aed"
    else:
        bg = "#ffffff"
        fg = "#0b1220"
        muted = "#4b5563"
        card = "#f8fafc"
        border = "#e5e7eb"
        sidebar_bg = "#f9fafb"
        sidebar_border = "#e5e7eb"
        chip_bg = "#eef2ff"
        chip_text = "#1f2937"
        placeholder = "#6b7280"
        alt_row = "#f3f4f6"
        accent = "#7c3aed"

    st.markdown(
        f"""
        <style>
        /* ===== App base ===== */
        .stApp {{
            background-color: {bg};
            color: {fg};
        }}
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
            color: {fg} !important;
        }}
        p, span, label, .stCaption, .stText {{
            color: {fg};
        }}

        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] > div:first-child {{
            background: {sidebar_bg};
            border-right: 1px solid {sidebar_border};
        }}
        [data-testid="stSidebar"] * {{
            color: {fg};
        }}
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stCaption {{
            color: {fg} !important;
        }}
        /* Inputs: text, number */
        [data-testid="stSidebar"] input[type="text"],
        [data-testid="stSidebar"] input[type="search"],
        [data-testid="stSidebar"] input[type="number"],
        [data-testid="stSidebar"] textarea {{
            background: {card} !important;
            color: {fg} !important;
            border: 1px solid {border} !important;
        }}
        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {{
            color: {placeholder} !important;
            opacity: 1;
        }}
        /* Selects y Multiselect (BaseWeb) */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background: {card} !important;
            border: 1px solid {border} !important;
            color: {fg} !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="select"] * {{
            color: {fg} !important;
        }}
        /* Dropdown del select */
        [data-baseweb="popover"] {{ 
            background: {card} !important;
            border: 1px solid {border} !important;
        }}
        [data-baseweb="menu"] div {{
            background: {card} !important;
            color: {fg} !important;
        }}
        /* Chips del multiselect */
        [data-testid="stSidebar"] [data-baseweb="tag"] {{
            background: {chip_bg} !important;
            color: {chip_text} !important;
            border-color: transparent !important;
        }}
        /* Botones en sidebar */
        [data-testid="stSidebar"] .stButton>button {{
            border: 1px solid {border};
            color: {fg};
            background: {card};
        }}
        [data-testid="stSidebar"] .stButton>button:hover {{
            border-color: {accent};
        }}
        /* Divisores */
        [data-testid="stSidebar"] hr {{
            border-color: {border};
        }}

        /* ===== Tabs ===== */
        .stTabs [data-baseweb="tab-list"] button {{
            color: {fg} !important;
            background: transparent;
            border-bottom: 1px solid {border} !important;
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom: 2px solid {accent} !important;
            color: {fg} !important;
        }}

        /* ===== Buttons (main area) ===== */
        .stButton>button {{
            border: 1px solid {border};
            color: {fg};
            background: {card};
        }}
        .stButton>button:hover {{
            border-color: {accent};
        }}

        /* ===== Métricas ===== */
        [data-testid="stMetric"] label {{
            color: {muted} !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {fg} !important;
        }}

        /* ===== Dataframe ===== */
        [data-testid="stDataFrame"] {{
            background: {card} !important;
            border: 1px solid {border};
            border-radius: 10px;
            overflow: hidden;
        }}
        [data-testid="stDataFrame"] .rowWidget:nth-child(even) {{
            background: {alt_row} !important;
        }}

        /* Expander + Code blocks */
        .streamlit-expanderHeader {{ color: {fg} !important; }}
        .stCodeBlock, .st-emotion-cache-16txtl3 {{
            color: {fg} !important;
            background: {card} !important;
            border: 1px solid {border} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def style_fig(fig, dark: bool):
    """Ajustes de contraste para todas las figuras Plotly."""
    if dark:
        paper_bg = "#0f1115"; plot_bg = "#0f1115"
        grid = "#2a2f3a"; axis = "#cbd5e1"; font = "#e6e6e6"; template = "plotly_dark"
    else:
        paper_bg = "#ffffff"; plot_bg = "#ffffff"
        grid = "#d1d5db"; axis = "#111827"; font = "#0b1220"; template = "plotly_white"

    fig.update_layout(
        template=template,
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=font),
        xaxis=dict(gridcolor=grid, zerolinecolor=grid, linecolor=axis,
                   tickfont=dict(color=axis), titlefont=dict(color=axis)),
        yaxis=dict(gridcolor=grid, zerolinecolor=grid, linecolor=axis,
                   tickfont=dict(color=axis), titlefont=dict(color=axis)),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420
    )
    return fig

def ticker_emoji(tk: str) -> str:
    tk = tk.upper()
    mapping = {
        "AAPL": "🍎", "MSFT": "🪟", "TSLA": "🚗", "NVDA": "🧠",
        "AMZN": "📦", "GOOGL": "🔍", "GOOG": "🔎", "META": "📱",
        "NFLX": "🎬", "JPM": "🏦", "XOM": "🛢️", "KO": "🥤",
        "DIS": "🏰", "SPY": "📊", "QQQ": "💹", "BTC-USD": "₿",
        "ETH-USD": "♦️",
    }
    return mapping.get(tk, "📈")

def market_summary(source_key: str):
    tickers = ["SPY", "QQQ", "BTC-USD"]
    names = {"SPY": "S&P 500 (SPY)", "QQQ": "Nasdaq 100 (QQQ)", "BTC-USD": "Bitcoin"}
    cols = st.columns(3)
    for i, tk in enumerate(tickers):
        try:
            df = price_history(tk, period="1y", interval="1d", source=source_key)
            if df.empty or len(df) < 2:
                cols[i].metric(names[tk], "—", "—")
                continue
            last = df["Close"].iloc[-1]
            prev = df["Close"].iloc[-2]
            chg = (last / prev - 1.0) * 100.0
            cols[i].metric(names[tk], f"${last:,.2f}", f"{chg:+.2f}%")
        except Exception:
            cols[i].metric(names[tk], "—", "—")

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("### 📊 Finance Dashboard")

    # Modo oscuro/claro
    dark_mode = st.toggle("🌙 Modo oscuro", value=sget("dark_mode", True))
    sset("dark_mode", dark_mode)
    apply_theme(dark_mode)

    # Fuente de datos
    source_options = ["Auto (Yahoo→Stooq)", "Stooq (rápido)"]
    source_index = sget("source_index", 0)
    source_label = st.selectbox("Fuente de datos", source_options, index=source_index)
    sset("source_index", source_options.index(source_label))
    source_key = "auto" if source_label.startswith("Auto") else "stooq"

    # Lista de empresas frecuentes
    options = {
        "Apple (AAPL)": "AAPL",
        "Microsoft (MSFT)": "MSFT",
        "Tesla (TSLA)": "TSLA",
        "NVIDIA (NVDA)": "NVDA",
        "Amazon (AMZN)": "AMZN",
        "Alphabet/Google (GOOGL)": "GOOGL",
        "Alphabet/Google (GOOG)": "GOOG",
        "Meta (META)": "META",
        "Netflix (NFLX)": "NFLX",
        "JPMorgan (JPM)": "JPM",
        "ExxonMobil (XOM)": "XOM",
        "Coca-Cola (KO)": "KO",
        "Disney (DIS)": "DIS",
        "S&P 500 ETF (SPY)": "SPY",
        "Nasdaq 100 ETF (QQQ)": "QQQ",
        "Bitcoin (BTC-USD)": "BTC-USD",
        "Ethereum (ETH-USD)": "ETH-USD",
    }

    # Empresa seleccionada (persistente)
    default_label = sget("label", "Apple (AAPL)")
    label = st.selectbox("Empresa", list(options.keys()), index=list(options.keys()).index(default_label))
    sset("label", label)
    selected_ticker = options[label]

    # Ticker manual (persistente)
    custom = st.text_input("…o escribe otro ticker (opcional)", value=sget("custom", "")).upper().strip()
    sset("custom", custom)
    ticker = custom if custom else selected_ticker
    sset("ticker", ticker)

    # Imagen dinámica del ticker
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin:8px 0 16px 0;">
            <div style="font-size:42px;line-height:1">{ticker_emoji(ticker)}</div>
            <div style="font-weight:700;">{ticker}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Multiselect de comparativa (excluye el actual)
    peer_labels_all = [k for k, v in options.items() if v != ticker]
    saved_peers = [p for p in sget("peer_labels_sel", ["Microsoft (MSFT)", "NVIDIA (NVDA)"]) if p in peer_labels_all]
    peer_labels_sel = st.multiselect("Comparar con (elige uno o varios)", peer_labels_all, default=saved_peers)
    sset("peer_labels_sel", peer_labels_sel)
    peers = [options[lbl] for lbl in peer_labels_sel if options[lbl] != ticker]

    # Periodo e intervalo (persistentes)
    period_list = ["1y", "2y", "5y", "10y", "max"]
    interval_list = ["1d", "1wk", "1mo"]
    p_idx = sget("p_idx", 2)
    i_idx = sget("i_idx", 0)
    p_choice = st.selectbox("Periodo", period_list, index=min(p_idx, len(period_list)-1))
    i_choice = st.selectbox("Intervalo", interval_list, index=min(i_idx, len(interval_list)-1))
    sset("p_idx", period_list.index(p_choice))
    sset("i_idx", interval_list.index(i_choice))
    period, interval = p_choice, i_choice

    # Resumen de mercado
    st.markdown("---")
    st.subheader("📰 Resumen de mercado")
    market_summary(source_key)

    # Recargar datos (limpia caché)
    st.markdown("---")
    if st.button("🔄 Recargar datos", use_container_width=True):
        st.cache_data.clear()
        st.experimental_rerun()

    # Watchlist
    st.subheader("⭐ Watchlist")
    wl = load_watchlist()
    if st.button("➕ Añadir ticker a watchlist", use_container_width=True) and ticker:
        wl = sorted(set(wl + [ticker]))
        save_watchlist(wl)
        st.experimental_rerun()

    if wl:
        chosen = st.selectbox(
            "Selecciona un ticker de tu watchlist",
            wl,
            index=wl.index(ticker) if ticker in wl else 0,
            key="wl_select"
        )
        if st.button("➡️ Ir al seleccionado", use_container_width=True):
            sset("custom", "")
            sset("label", next((k for k, v in options.items() if v == chosen), "Apple (AAPL)"))
            st.experimental_rerun()

        remove = st.multiselect("Quitar de watchlist", wl, [])
        if st.button("🗑️ Quitar seleccionados", use_container_width=True) and remove:
            wl = [t for t in wl if t not in remove]
            save_watchlist(wl)
            st.experimental_rerun()
    else:
        st.caption("Tu watchlist está vacía.")

# =========================
# Header
# =========================
st.title("📊 Finance Dashboard")
st.caption("Precios, indicadores técnicos y (si están disponibles) fundamentales.")
st.write(f"**Ticker actual:** `{ticker}`")

# =========================
# Tabs dinámicas
# =========================
has_fund = fundamentals_available(ticker)
tab_names = ["Visión general", "Técnicos", "Comparativa"]
if has_fund:
    tab_names.insert(1, "Ratios")
    tab_names.insert(2, "Estados financieros")
tabs = st.tabs(tab_names)

def style_fig(fig, dark: bool):
    """Ajustes de contraste para todas las figuras Plotly."""
    if dark:
        paper_bg = "#0f1115"; plot_bg = "#0f1115"
        grid = "#2a2f3a"; axis = "#cbd5e1"; font = "#e6e6e6"; template = "plotly_dark"
    else:
        paper_bg = "#ffffff"; plot_bg = "#ffffff"
        grid = "#d1d5db"; axis = "#111827"; font = "#0b1220"; template = "plotly_white"
    fig.update_layout(
        template=template, paper_bgcolor=paper_bg, plot_bgcolor=plot_bg,
        font=dict(color=font),
        xaxis=dict(gridcolor=grid, zerolinecolor=grid, linecolor=axis,
                   tickfont=dict(color=axis), titlefont=dict(color=axis)),
        yaxis=dict(gridcolor=grid, zerolinecolor=grid, linecolor=axis,
                   tickfont=dict(color=axis), titlefont=dict(color=axis)),
        margin=dict(l=10, r=10, t=50, b=10), height=420
    ); return fig

# =========================
# Visión general
# =========================
with tabs[0]:
    with st.spinner("Cargando datos de precios..."):
        df = price_history(ticker, period=period, interval=interval, source=source_key)

    if df.empty:
        st.warning("No se pudieron cargar precios para el ticker indicado.")
    else:
        src = getattr(df, "attrs", {}).get("__source__", "desconocida")
        st.caption(f"Fuente de datos utilizada: **{src}**")

        if getattr(df, "attrs", {}).get("__demo__"):
            st.info("Mostrando **datos de ejemplo** (modo demo).")
        if getattr(df, "attrs", {}).get("__errors__"):
            with st.expander("Detalles técnicos (errores capturados)"):
                st.code(df.attrs["__errors__"], language="text")

        c1, c2, c3, c4 = st.columns(4)
        last_price = df["Close"].iloc[-1]
        y_last = df["Close"].resample("Y").last().pct_change().dropna()
        ytd_val = y_last.iloc[-1] if len(y_last) > 0 else df["Close"].pct_change().iloc[-252:].sum()
        vol21 = rolling_volatility(df, 21).dropna()
        vol21_val = vol21.iloc[-1] if len(vol21) else 0.0
        ret_ann = annual_returns(df)
        avg_ann = ret_ann.mean() if not ret_ann.empty else 0.0

        with c1: metric_card("Precio actual", f"${last_price:,.2f}")
        with c2: metric_card("Variación anual (últ.)", f"{(ytd_val * 100):.2f}%")
        with c3: metric_card("Volatilidad 21d (anualizada)", f"{(vol21_val * 100):.2f}%")
        with c4: metric_card("Rentabilidad anual media", f"{(avg_ann * 100):.2f}%")

        st.markdown("### Evolución del precio")
        df_reset = df.reset_index()
        if "Date" not in df_reset.columns:
            df_reset = df_reset.rename(columns={df_reset.columns[0]: "Date"})
        fig = px.line(df_reset, x="Date", y="Close", title=f"{ticker} – Precio de Cierre")
        fig = style_fig(fig, sget("dark_mode", True))
        st.plotly_chart(fig, use_container_width=True)

        # Descargas (CSV/PNG)
        csv_bytes = df_reset.to_csv(index=False).encode("utf-8")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("⬇️ Descargar precios (CSV)", data=csv_bytes,
                               file_name=f"{ticker}_price_history.csv", mime="text/csv")
        with col_dl2:
            try:
                png_bytes = io.BytesIO()
                fig.write_image(png_bytes, format="png")
                st.download_button("🖼️ Descargar gráfico (PNG)", data=png_bytes.getvalue(),
                                   file_name=f"{ticker}_price.png", mime="image/png")
            except Exception:
                st.caption("Para exportar a PNG instala `kaleido`.")

# =========================
# Ratios
# =========================
if has_fund:
    with tabs[1]:
        r = compute_ratios(ticker)
        if all([pd.isna(v) for v in r.values()]):
            st.info("No hay ratios disponibles para este ticker en yfinance.")
        else:
            c1, c2, c3 = st.columns(3)
            c4, c5, c6 = st.columns(3)

            def fmt(val, percent=False):
                if val is None or (isinstance(val, float) and pd.isna(val)):
                    return "—"
                return f"{val * 100:.2f}%" if percent else f"{val:.2f}"

            c1.metric("P/E", fmt(r.get("P/E")))
            c2.metric("P/S", fmt(r.get("P/S")))
            c3.metric("Current Ratio", fmt(r.get("Current Ratio")))
            c4.metric("ROE", fmt(r.get("ROE"), percent=True))
            c5.metric("ROA", fmt(r.get("ROA"), percent=True))
            c6.write("")
            st.caption("Fuente: yfinance (si está disponible para el ticker).")

# =========================
# Estados financieros
# =========================
if has_fund:
    with tabs[2]:
        fin = get_financials(ticker)
        if not any([not df.empty for df in fin.values()]):
            st.info("No hay estados financieros disponibles para este ticker en yfinance.")
        else:
            colA, colB, colC = st.columns(3)
            with colA:
                st.subheader("Income Statement")
                st.dataframe(fin.get("income"))
            with colB:
                st.subheader("Balance Sheet")
                st.dataframe(fin.get("balance"))
            with colC:
                st.subheader("Cash Flow")
                st.dataframe(fin.get("cashflow"))

# =========================
# Técnicos
# =========================
with tabs[-2 if has_fund else 1]:
    with st.spinner("Calculando indicadores técnicos..."):
        df = price_history(ticker, period=period, interval=interval, source=source_key)
        tech = technicals(df)

    if tech.empty:
        st.warning("No se pudieron calcular técnicos (no hay precios).")
    else:
        st.markdown("### SMA/EMA y Bandas de Bollinger")
        dfr = tech.reset_index()
        if "Date" not in dfr.columns:
            dfr = dfr.rename(columns={dfr.columns[0]: "Date"})
        fig_t = px.line(
            dfr,
            x="Date",
            y=["Close", "SMA20", "SMA50", "EMA12", "EMA26", "BB_Up", "BB_Mid", "BB_Lo"],
            title=f"{ticker} – Técnicos (SMA/EMA/Bollinger)"
        )
        fig_t = style_fig(fig_t, sget("dark_mode", True))
        st.plotly_chart(fig_t, use_container_width=True)

        st.markdown("### RSI(14)")
        fig_rsi = px.line(dfr, x="Date", y="RSI14", title="RSI(14)")
        fig_rsi.add_hline(y=70, line_dash="dash")
        fig_rsi.add_hline(y=30, line_dash="dash")
        fig_rsi = style_fig(fig_rsi, sget("dark_mode", True))
        fig_rsi.update_layout(height=260)
        st.plotly_chart(fig_rsi, use_container_width=True)

# =========================
# Comparativa (con descargas)
# =========================
with tabs[-1]:
    peer_list = [ticker] + [p for p in peers if p != ticker]
    dedup = []
    for tk in peer_list:
        if tk not in dedup:
            dedup.append(tk)
    peer_list = dedup

    if len(peer_list) <= 1:
        st.info("Elige al menos un ticker en 'Comparar con' para construir la comparativa.")
    else:
        combined = []
        for tk in peer_list:
            dfi = price_history(tk, period=period, interval=interval, source=source_key)
            if dfi.empty:
                continue
            tmp = dfi[["Close"]].rename(columns={"Close": tk})
            combined.append(tmp)

        if combined:
            merged = pd.concat(combined, axis=1).dropna()
            merged = merged.loc[:, ~merged.columns.duplicated()]
            rel = merged / merged.iloc[0] - 1.0

            rel_reset = rel.reset_index()
            if "Date" not in rel_reset.columns:
                rel_reset = rel_reset.rename(columns={rel_reset.columns[0]: "Date"})

            st.markdown("### Rentabilidad relativa (desde el inicio del periodo)")
            fig3 = px.line(rel_reset, x="Date", y=list(rel.columns), title="Comparativa de rentabilidades")
            fig3 = style_fig(fig3, sget("dark_mode", True))
            st.plotly_chart(fig3, use_container_width=True)

            colc1, colc2 = st.columns(2)
            with colc1:
                comp_csv = rel_reset.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Descargar comparativa (CSV)", data=comp_csv,
                                   file_name=f"comparativa_{'_'.join(rel.columns)}.csv", mime="text/csv")
            with colc2:
                try:
                    png_bytes3 = io.BytesIO()
                    fig3.write_image(png_bytes3, format="png")
                    st.download_button("🖼️ Descargar comparativa (PNG)", data=png_bytes3.getvalue(),
                                       file_name=f"comparativa_{'_'.join(rel.columns)}.png", mime="image/png")
                except Exception:
                    st.caption("Para exportar la imagen instala el paquete `kaleido`.")
        else:
            st.warning("No se pudo construir la comparativa con los tickers dados.")
