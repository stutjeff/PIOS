import re
import pandas as pd
from core.storage import load_csv, save_csv

WATCHLIST_FILE = 'watchlist.csv'
REQUIRED_COLUMNS = ['ticker','name','market','industry','sub_industry','theme','main_products','business_model','customers','suppliers','competitors','moat','management','key_questions','status']
MARKET_ORDER = {'台股':1,'美股':2,'日股':3}

def normalize_ticker(ticker: str, market: str = '') -> str:
    t = str(ticker).strip().upper().replace(' ', '')
    if not t: return ''
    if market == '台股' and re.fullmatch(r'\d{4}', t): return f'{t}.TW'
    if market == '日股' and re.fullmatch(r'\d{4}', t): return f'{t}.T'
    if market == '美股': return t.replace('.US','')
    return t

def ticker_num(ticker: str) -> int:
    m = re.search(r'\d+', str(ticker))
    return int(m.group()) if m else 999999

def sort_watchlist(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['ticker'] = df.apply(lambda r: normalize_ticker(r['ticker'], r['market']), axis=1)
    df['_market'] = df['market'].map(MARKET_ORDER).fillna(99)
    df['_num'] = df['ticker'].apply(ticker_num)
    df['_alpha'] = df['ticker'].astype(str).str.upper()
    df = df.sort_values(['_market','_num','_alpha','name'])
    return df.drop(columns=['_market','_num','_alpha'])

def load_watchlist() -> pd.DataFrame:
    return sort_watchlist(load_csv(WATCHLIST_FILE, REQUIRED_COLUMNS))

def save_watchlist(df: pd.DataFrame):
    save_csv(WATCHLIST_FILE, sort_watchlist(df))
