from typing import Optional
import requests
from bs4 import BeautifulSoup
import streamlit as st

BASE_URL = 'https://finance.biggo.com.tw/quote'
HEADERS = {'User-Agent':'Mozilla/5.0 AppleWebKit/537.36 Chrome/126 Safari/537.36','Accept-Language':'zh-TW,zh;q=0.9,en;q=0.8'}

def _fetch_text(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.get_text('\n', strip=True)

def _find_after(text: str, label: str, window: int = 120) -> Optional[str]:
    idx = text.find(label)
    if idx < 0: return None
    chunk = text[idx + len(label): idx + len(label) + window]
    lines = [x.strip() for x in chunk.splitlines() if x.strip()]
    return lines[0] if lines else None

@st.cache_data(ttl=1800)
def get_biggo_overview(ticker: str):
    url = f'{BASE_URL}/{ticker}'
    try:
        text = _fetch_text(url)
        return {'source':'BigGo','url':url,'market_cap':_find_after(text,'市值'),'pe':_find_after(text,'本益比（近十二個月）'),'eps':_find_after(text,'每股盈餘（近十二個月）'),'dividend_yield':_find_after(text,'預估股息與殖利率'),'industry':_find_after(text,'產業分類'),'report_date':_find_after(text,'財報公布日')}
    except Exception as e:
        return {'source':'BigGo','url':url,'error':str(e)}

@st.cache_data(ttl=1800)
def get_biggo_financial(ticker: str):
    url = f'{BASE_URL}/{ticker}/financial'
    try:
        text = _fetch_text(url)
        return {'source':'BigGo','url':url,'revenue_hint':_find_after(text,'營收'),'gross_margin':_find_after(text,'毛利率'),'roe':_find_after(text,'ROE'),'debt_ratio':_find_after(text,'負債比')}
    except Exception as e:
        return {'source':'BigGo','url':url,'error':str(e)}
