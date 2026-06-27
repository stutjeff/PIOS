import streamlit as st
import yfinance as yf
@st.cache_data(ttl=900)
def get_price_data(ticker):
    try:
        d=yf.download(ticker,period='1y',interval='1d',auto_adjust=True,progress=False)
        if d.empty or len(d)<5: return None
        c=d['Close']; v=d['Volume']; price=float(c.iloc[-1]); prev=float(c.iloc[-2]); high=float(c.max()); avgv=float(v.tail(20).mean()); lv=float(v.iloc[-1])
        return {'source':'yfinance','price':price,'daily_change':(price/prev-1)*100,'high_52w':high,'drop_from_high':(price/high-1)*100,'volume_ratio':lv/avgv if avgv>0 else 0}
    except Exception: return None
@st.cache_data(ttl=3600)
def get_info(ticker):
    try:
        i=yf.Ticker(ticker).info or {}
        return {'source':'yfinance','market_cap':i.get('marketCap'),'pe':i.get('trailingPE'),'forward_pe':i.get('forwardPE'),'pb':i.get('priceToBook'),'dividend_yield':i.get('dividendYield'),'roe':i.get('returnOnEquity'),'revenue_growth':i.get('revenueGrowth')}
    except Exception: return {'source':'yfinance'}
