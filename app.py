import time
from datetime import datetime
from urllib.parse import quote
import pandas as pd
import requests
import yfinance as yf

HEADERS = {'User-Agent':'Mozilla/5.0 AppleWebKit/537.36 Chrome/126 Safari/537.36','Accept-Language':'zh-TW,zh;q=0.9,en;q=0.8'}

def _result(source, dataset, ok, rows=0, ms=0, message='', url=''):
    return {'source':source,'dataset':dataset,'status':'✅ 成功' if ok else '❌ 失敗','rows':rows,'response_ms':round(ms,0),'checked_at':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'message':str(message)[:300],'url':url}

def check_url_json(source, dataset, url, rows_key=None, timeout=12):
    start = time.perf_counter()
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        ms = (time.perf_counter()-start)*1000
        r.raise_for_status(); data = r.json(); rows = 0
        if isinstance(data, list): rows = len(data)
        elif isinstance(data, dict):
            if rows_key and isinstance(data.get(rows_key), list): rows = len(data.get(rows_key))
            elif isinstance(data.get('data'), list): rows = len(data.get('data'))
            else: rows = len(data.keys())
        return _result(source,dataset,True,rows,ms,'OK',url)
    except Exception as e:
        ms = (time.perf_counter()-start)*1000
        return _result(source,dataset,False,0,ms,e,url)

def check_yfinance(ticker='2330.TW'):
    start=time.perf_counter()
    try:
        data=yf.download(ticker, period='5d', interval='1d', progress=False, auto_adjust=True)
        ms=(time.perf_counter()-start)*1000
        return _result('yfinance',f'{ticker} 5日股價',not data.empty,len(data),ms,'OK' if not data.empty else 'empty','')
    except Exception as e:
        ms=(time.perf_counter()-start)*1000
        return _result('yfinance',f'{ticker} 5日股價',False,0,ms,e,'')

def check_finmind(stock_id='2330'):
    url=f'https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockPrice&data_id={stock_id}&start_date=2024-01-01'
    return check_url_json('FinMind',f'{stock_id} 股價',url,rows_key='data',timeout=15)

def check_twse_openapi_monthly_revenue():
    return check_url_json('TWSE OpenAPI','上市公司每月營收','https://openapi.twse.com.tw/v1/opendata/t187ap05_L',timeout=15)

def check_twse_openapi_company_profile():
    return check_url_json('TWSE OpenAPI','上市公司基本資料','https://openapi.twse.com.tw/v1/opendata/t187ap03_L',timeout=15)

def check_twse_stock_day(stock_no='2330'):
    url=f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20250101&stockNo={stock_no}'
    return check_url_json('TWSE',f'{stock_no} 個股日成交',url,rows_key='data',timeout=15)

def check_biggo(ticker='2330.TW'):
    url=f'https://finance.biggo.com.tw/quote/{quote(ticker)}'
    start=time.perf_counter()
    try:
        r=requests.get(url,headers=HEADERS,timeout=10); ms=(time.perf_counter()-start)*1000
        ok = r.status_code == 200 and len(r.text) > 1000
        return _result('BigGo',f'{ticker} 個股頁',ok,len(r.text),ms,f'HTTP {r.status_code}',url)
    except Exception as e:
        ms=(time.perf_counter()-start)*1000
        return _result('BigGo',f'{ticker} 個股頁',False,0,ms,e,url)

def run_health_check(stock_id='2330', yf_ticker='2330.TW', biggo_ticker='2330.TW'):
    checks=[check_twse_openapi_monthly_revenue(),check_twse_openapi_company_profile(),check_twse_stock_day(stock_id),check_finmind(stock_id),check_yfinance(yf_ticker),check_biggo(biggo_ticker)]
    return pd.DataFrame(checks)
