from __future__ import annotations

import traceback
import concurrent.futures as cf

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# Stooq vía pandas-datareader (sin API key)
try:
    import pandas_datareader.data as web
    _HAS_STOOQ = True
except Exception:
    _HAS_STOOQ = False


# =========================
# Helpers para precio
# =========================

def _yahoo_download(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """Intenta primero yf.download; si viene vacío, intenta Ticker().history()."""
    # 1) download
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except Exception:
        pass
    # 2) history
    try:
        t = yf.Ticker(ticker.upper())
        df = t.history(period=period, interval=interval, auto_adjust=True)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except Exception:
        pass
    return pd.DataFrame()


def _yahoo_with_timeout(ticker: str, period: str, interval: str, timeout_s: float = 2.0) -> pd.DataFrame:
    """Ejecuta Yahoo con timeout duro; si se agota, devuelve DF vacío (para no colgar la UI)."""
    try:
        with cf.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(_yahoo_download, ticker, period, interval)
            return fut.result(timeout=timeout_s)
    except Exception:
        return pd.DataFrame()


def _stooq_fetch(ticker: str, period: str) -> pd.DataFrame:
    """Carga diario desde Stooq y recorta ventana aproximada según 'period'. Sin API key."""
    if not _HAS_STOOQ:
        return pd.DataFrame()
    try:
        df = web.DataReader(ticker, "stooq")
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.sort_index()  # asegurar ascendente
        # recorte aproximado por periodo (diario)
        years_map = {"1y": 252, "2y": 504, "5y": 1260, "10y": 2520, "max": len(df)}
        n = years_map.get(period, 1260)
        df = df.tail(min(n, len(df)))
        return df
    except Exception:
        return pd.DataFrame()


def _demo_series(tk: str, period: str, interval: str) -> pd.DataFrame:
    """Serie sintética determinista que RESPETA period/interval para que el UI no quede vacío."""
    years_map = {"1y": 1, "2y": 2, "5y": 5, "10y": 10, "max": 10}
    yrs = years_map.get(period, 5)

    if interval == "1d":
        n = int(252 * yrs); freq = "B"; dt_step = 1 / 252
    elif interval == "1wk":
        n = int(52 * yrs);  freq = "W-FRI"; dt_step = 1 / 52
    else:  # "1mo"
        n = int(12 * yrs);  freq = "M"; dt_step = 1 / 12

    end = pd.Timestamp.today().normalize()
    idx = pd.date_range(end=end, periods=max(n, 30), freq=freq)

    seed = (abs(hash(f"{tk}-{period}-{interval}")) % (2**32))
    rng = np.random.default_rng(seed)
    mu, sigma = 0.08, 0.22
    shocks = rng.normal((mu - 0.5 * sigma**2) * dt_step, sigma * np.sqrt(dt_step), size=len(idx))
    price = 100 * np.exp(np.cumsum(shocks))
    df = pd.DataFrame({"Close": price}, index=idx)
    df["Return"] = df["Close"].pct_change()
    df.attrs["__demo__"] = True
    df.attrs["__source__"] = "demo"
    return df


# =========================
# API principal de precios
# =========================

@st.cache_data(show_spinner=False, ttl=300)  # 5 minutos
def price_history(ticker: str, period: str = "5y", interval: str = "1d", source: str = "auto") -> pd.DataFrame:
    """
    Devuelve histórico con columnas 'Close' y 'Return'.
    Guarda la fuente usada en df.attrs['__source__'] ∈ {'yahoo','stooq','demo'}.

    Parámetro 'source':
      - 'auto'  → Yahoo (timeout 2s) → Stooq → Demo
      - 'stooq' → Solo Stooq → Demo
    """
    # Forzar Stooq si lo pide el usuario
    if source == "stooq":
        df = _stooq_fetch(ticker, period)
        if isinstance(df, pd.DataFrame) and not df.empty:
            df = df.rename(columns={c: c.title() for c in df.columns})
            if "Close" in df.columns:
                df["Return"] = df["Close"].pct_change()
                df.attrs["__source__"] = "stooq"
                return df
        return _demo_series(ticker, period, interval)

    # AUTO: Yahoo con timeout → Stooq → Demo
    errors: list[str] = []
    try:
        df = _yahoo_with_timeout(ticker, period, interval, timeout_s=2.0)
    except Exception as e:
        df = pd.DataFrame()
        errors += [f"yahoo timeout error: {repr(e)}", traceback.format_exc()]

    if isinstance(df, pd.DataFrame) and not df.empty:
        df = df.rename(columns={c: c.title() for c in df.columns})
        if "Close" in df.columns:
            df["Return"] = df["Close"].pct_change()
            df.attrs["__source__"] = "yahoo"
            return df

    # Stooq fallback
    df = _stooq_fetch(ticker, period)
    if isinstance(df, pd.DataFrame) and not df.empty:
        df = df.rename(columns={c: c.title() for c in df.columns})
        if "Close" in df.columns:
            df["Return"] = df["Close"].pct_change()
            df.attrs["__source__"] = "stooq"
            return df

    # Demo final
    demo = _demo_series(ticker, period, interval)
    if errors:
        demo.attrs["__errors__"] = "\n".join(errors[-3:])
    return demo


@st.cache_data(show_spinner=False, ttl=600)
def annual_returns(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    return df["Close"].resample("Y").last().pct_change().dropna()


@st.cache_data(show_spinner=False, ttl=600)
def rolling_volatility(df: pd.DataFrame, window: int = 21) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    return df["Return"].rolling(window).std() * np.sqrt(252)


# =========================
# Fundamentales (yfinance)
# =========================

def get_ticker(ticker: str) -> yf.Ticker:
    return yf.Ticker(ticker.upper())


@st.cache_data(show_spinner=False, ttl=1200)
def get_financials(ticker: str) -> dict[str, pd.DataFrame]:
    """
    Usa yfinance. Puede venir vacío (depende del ticker/disponibilidad).
    Devuelve dict con DataFrames (posiblemente vacíos).
    """
    t = get_ticker(ticker)

    def safe_df(attr_name: str) -> pd.DataFrame:
        df = getattr(t, attr_name, pd.DataFrame())
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
        return pd.DataFrame()

    income = safe_df("income_stmt")
    balance = safe_df("balance_sheet")
    cashflow = safe_df("cashflow")

    # Fallback "legacy"
    if income.empty:
        legacy = safe_df("financials")
        if not legacy.empty:
            income = legacy

    return {"income": income, "balance": balance, "cashflow": cashflow}


@st.cache_data(show_spinner=False, ttl=1200)
def compute_ratios(ticker: str) -> dict[str, float]:
    """
    Intenta ratios vía yfinance.get_info().
    Si no están, calcula ROE/ROA/Current desde estados (si existen).
    """
    ratios = {"P/E": np.nan, "P/S": np.nan, "Current Ratio": np.nan, "ROE": np.nan, "ROA": np.nan}

    t = get_ticker(ticker)
    info_dict = {}
    try:
        if hasattr(t, "get_info") and callable(t.get_info):
            info_dict = t.get_info() or {}
    except Exception:
        info_dict = {}

    # P/E y P/S desde info()
    try:
        pe = info_dict.get("trailingPE") or info_dict.get("forwardPE")
        if pe is not None:
            ratios["P/E"] = float(pe)
    except Exception:
        pass

    try:
        ps = info_dict.get("priceToSalesTrailing12Months")
        if ps is not None:
            ratios["P/S"] = float(ps)
    except Exception:
        pass

    fin = get_financials(ticker)
    income, balance = fin["income"], fin["balance"]

    def latest(df: pd.DataFrame, row_name: str):
        if df.empty or row_name not in df.index:
            return np.nan
        vals = pd.to_numeric(df.loc[row_name].dropna(), errors="coerce").dropna()
        return float(vals.iloc[-1]) if not vals.empty else np.nan

    net_income = latest(income, "Net Income")
    total_equity = latest(balance, "Total Stockholder Equity")
    total_assets = latest(balance, "Total Assets")
    total_current_assets = latest(balance, "Total Current Assets")
    total_current_liab = latest(balance, "Total Current Liabilities")

    # ROE / ROA / Current Ratio desde estados (si hay)
    try:
        if not np.isnan(net_income) and not np.isnan(total_equity) and total_equity != 0:
            ratios["ROE"] = float(net_income) / float(total_equity)
    except Exception:
        pass
    try:
        if not np.isnan(net_income) and not np.isnan(total_assets) and total_assets != 0:
            ratios["ROA"] = float(net_income) / float(total_assets)
    except Exception:
        pass
    try:
        if not np.isnan(total_current_assets) and not np.isnan(total_current_liab) and total_current_liab != 0:
            ratios["Current Ratio"] = float(total_current_assets) / float(total_current_liab)
    except Exception:
        pass

    return ratios


def fundamentals_available(ticker: str) -> bool:
    """Devuelve True si hay al menos algún ratio o alguna tabla de estados con datos."""
    r = compute_ratios(ticker)
    any_ratio = any(pd.notna(v) for v in r.values())
    fin = get_financials(ticker)
    any_stmt = any((isinstance(df, pd.DataFrame) and not df.empty) for df in fin.values())
    return bool(any_ratio or any_stmt)


# =========================
# Indicadores técnicos
# =========================

@st.cache_data(show_spinner=False, ttl=600)
def technicals(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula SMA20/50, EMA12/26, Bollinger(20,2) y RSI(14)."""
    if df.empty:
        return df
    out = df.copy()
    close = out["Close"]

    out["SMA20"] = close.rolling(20).mean()
    out["SMA50"] = close.rolling(50).mean()
    out["EMA12"] = close.ewm(span=12, adjust=False).mean()
    out["EMA26"] = close.ewm(span=26, adjust=False).mean()

    mb = close.rolling(20).mean()
    sd = close.rolling(20).std()
    out["BB_Mid"] = mb
    out["BB_Up"] = mb + 2 * sd
    out["BB_Lo"] = mb - 2 * sd

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    roll_up = gain.rolling(14).mean()
    roll_down = loss.rolling(14).mean()
    rs = roll_up / (roll_down.replace(0, np.nan))
    out["RSI14"] = 100 - (100 / (1 + rs))

    return out
