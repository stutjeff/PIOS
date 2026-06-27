from typing import Optional
import requests, streamlit as st
from bs4 import BeautifulSoup
BASE='https://finance.biggo.com.tw/quote'
HEADERS={'User-Agent':'Mozilla/5.0 AppleWebKit/537.36 Chrome/126 Safari/537.36','Accept-Language':'zh-TW,zh;q=0.9,en;q=0.8'}
def _text(url):
    r=requests.get(url,headers=HEADERS,timeout=15); r.raise_for_status(); return BeautifulSoup(r.text,'html.parser').get_text('\n',strip=True)
def _after(text,label,window=120)->Optional[str]:
    i=text.find(label)
    if i<0: return None
    lines=[x.strip() for x in text[i+len(label):i+len(label)+window].splitlines() if x.strip()]
    return lines[0] if lines else None
@st.cache_data(ttl=3600)
def get_biggo_overview(ticker):
    url=f'{BASE}/{ticker}'
    try:
        t=_text(url)
        return {'source':'BigGo','url':url,'market_cap':_after(t,'市值'),'pe':_after(t,'本益比（近十二個月）'),'eps':_after(t,'每股盈餘（近十二個月）'),'dividend_yield':_after(t,'預估股息與殖利率'),'industry':_after(t,'產業分類'),'report_date':_after(t,'財報公布日'),'chairman':_after(t,'董事長'),'founded_date':_after(t,'成立日期'),'listed_date':_after(t,'上市日期')}
    except Exception as e: return {'source':'BigGo','url':url,'error':str(e)}
@st.cache_data(ttl=3600)
def get_biggo_financial(ticker):
    url=f'{BASE}/{ticker}/financial'
    try:
        t=_text(url)
        return {'source':'BigGo','url':url,'revenue_hint':_after(t,'營收'),'gross_margin':_after(t,'毛利率'),'operating_margin':_after(t,'營業利益率'),'net_margin':_after(t,'淨利率'),'roe':_after(t,'ROE'),'debt_ratio':_after(t,'負債比')}
    except Exception as e: return {'source':'BigGo','url':url,'error':str(e)}
