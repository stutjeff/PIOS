import streamlit as st
import yfinance as yf

@st.cache_data(ttl=900)
def get_price_data(ticker: str):
    try:
        data = yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False)
        if data.empty or len(data) < 5: return None
        close = data['Close']; volume = data['Volume']
        price = float(close.iloc[-1]); prev = float(close.iloc[-2]); high = float(close.max())
        avg_vol = float(volume.tail(20).mean()); latest_vol = float(volume.iloc[-1])
        return {'source':'yfinance','price':price,'daily_change':(price/prev-1)*100,'high_52w':high,'drop_from_high':(price/high-1)*100,'volume_ratio':latest_vol/avg_vol if avg_vol>0 else 0}
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_info(ticker: str):
    try:
        info = yf.Ticker(ticker).info or {}
        return {'source':'yfinance','market_cap':info.get('marketCap'),'pe':info.get('trailingPE'),'forward_pe':info.get('forwardPE'),'pb':info.get('priceToBook'),'dividend_yield':info.get('dividendYield'),'roe':info.get('returnOnEquity'),'revenue_growth':info.get('revenueGrowth')}
    except Exception:
        return {'source':'yfinance'}
