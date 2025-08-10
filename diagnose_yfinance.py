import yfinance as yf, pandas as pd

print("Testing yfinance download('AAPL', period='1mo', interval='1d')...")
try:
    df = yf.download("AAPL", period="1mo", interval="1d", auto_adjust=True, progress=False)
    print("Rows:", 0 if df is None else len(df))
    print(df.head())
except Exception as e:
    print("download() error:", repr(e))

print("\nTesting Ticker('AAPL').history('1mo','1d')...")
try:
    t = yf.Ticker("AAPL")
    df2 = t.history(period="1mo", interval="1d", auto_adjust=True)
    print("Rows:", 0 if df2 is None else len(df2))
    print(df2.head())
except Exception as e:
    print("history() error:", repr(e))

print("\nIf both are zero rows, it's likely a network/proxy/SSL issue blocking Yahoo endpoints.")