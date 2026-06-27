import pandas as pd
import streamlit as st
def section(t,d=None):
    st.markdown(f'## {t}')
    if d: st.caption(d)
def fmt_num(v):
    if v is None or pd.isna(v): return '—'
    try:
        v=float(v)
        if abs(v)>=1_000_000_000_000: return f'{v/1_000_000_000_000:.2f} 兆'
        if abs(v)>=100_000_000: return f'{v/100_000_000:.2f} 億'
        if abs(v)>=10_000: return f'{v/10_000:.2f} 萬'
        return f'{v:.2f}'
    except Exception: return str(v)
def fmt_pct(v,already_pct=False):
    if v is None or pd.isna(v): return '—'
    try:
        v=float(v); v=v if already_pct else v*100; return f'{v:.2f}%'
    except Exception: return str(v)
def status_badge(s):
    return {'核心觀察':'🔵 核心觀察','持續追蹤':'🟢 持續追蹤','觀察':'🟡 觀察','暫停追蹤':'⚪ 暫停追蹤'}.get(str(s),str(s))
def questions():
    return [('能力圈','我真的懂這家公司怎麼賺錢嗎？'),('護城河','它的優勢是技術、客戶、成本、法規，還是我想像出來的？'),('安全邊際','如果我錯了，損失能不能承受？'),('反向思考','什麼情況會證明我的投資假設是錯的？'),('第一性原理','這個需求的底層原因是什麼？'),('確認偏誤','我是不是只看支持自己想法的資料？')]
