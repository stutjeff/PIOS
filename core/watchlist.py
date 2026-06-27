import re
import pandas as pd
from pathlib import Path
DATA_DIR=Path('data'); DATA_DIR.mkdir(exist_ok=True)
COLS=['ticker','name','market','industry','sub_industry','theme','main_products','business_model','customers','suppliers','competitors','moat','management','key_questions','status']
ORDER={'台股':1,'美股':2,'日股':3}
def normalize_ticker(ticker, market=''):
    t=str(ticker).strip().upper().replace(' ','')
    if market=='台股' and re.fullmatch(r'\d{4}',t): return t+'.TW'
    if market=='日股' and re.fullmatch(r'\d{4}',t): return t+'.T'
    if market=='美股': return t.replace('.US','')
    return t
def _num(t):
    m=re.search(r'\d+',str(t)); return int(m.group()) if m else 999999
def sort_watchlist(df):
    df=df.copy()
    for c in COLS:
        if c not in df.columns: df[c]=''
    df=df[COLS]
    df['ticker']=df.apply(lambda r: normalize_ticker(r['ticker'],r['market']),axis=1)
    df['_m']=df['market'].map(ORDER).fillna(99); df['_n']=df['ticker'].apply(_num); df['_a']=df['ticker'].astype(str)
    return df.sort_values(['_m','_n','_a','name']).drop(columns=['_m','_n','_a'])
def load_watchlist():
    p=DATA_DIR/'watchlist.csv'
    if not p.exists():
        pd.DataFrame(columns=COLS).to_csv(p,index=False)
    return sort_watchlist(pd.read_csv(p))
def save_watchlist(df):
    sort_watchlist(df).to_csv(DATA_DIR/'watchlist.csv',index=False)
