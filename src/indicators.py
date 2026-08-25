"""Technical indicators computed from a price history DataFrame with a 'Close' column."""
import pandas as pd


def sma(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window).mean()


def ema(close: pd.Series, span: int) -> pd.Series:
    return close.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def bollinger_bands(close: pd.Series, window: int = 20, num_std: float = 2.0):
    mid = sma(close, window)
    std = close.rolling(window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower


def compute_all(df: pd.DataFrame) -> dict:
    """Returns latest-value snapshot of key indicators for a price history df."""
    close = df["Close"]
    sma50 = sma(close, 50)
    sma200 = sma(close, 200)
    rsi14 = rsi(close, 14)
    macd_line, signal_line, hist = macd(close)
    upper, mid, lower = bollinger_bands(close)

    latest_close = close.iloc[-1]
    high_52w = close.tail(252).max()
    low_52w = close.tail(252).min()

    return {
        "close": latest_close,
        "sma50": sma50.iloc[-1] if not sma50.isna().all() else None,
        "sma200": sma200.iloc[-1] if not sma200.isna().all() else None,
        "rsi14": rsi14.iloc[-1] if not rsi14.isna().all() else None,
        "macd": macd_line.iloc[-1],
        "macd_signal": signal_line.iloc[-1],
        "macd_hist": hist.iloc[-1],
        "bb_upper": upper.iloc[-1],
        "bb_lower": lower.iloc[-1],
        "high_52w": high_52w,
        "low_52w": low_52w,
        "pct_from_52w_high": (latest_close - high_52w) / high_52w * 100,
        "pct_from_52w_low": (latest_close - low_52w) / low_52w * 100,
        "golden_cross": bool(sma50.iloc[-1] and sma200.iloc[-1] and sma50.iloc[-1] > sma200.iloc[-1]),
    }
