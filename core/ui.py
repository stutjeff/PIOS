import pandas as pd
import streamlit as st

def section(title, desc=None):
    st.markdown(f'## {title}')
    if desc: st.caption(desc)

def fmt_num(value):
    if value is None or pd.isna(value): return '—'
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000_000: return f'{value/1_000_000_000_000:.2f} 兆'
        if abs(value) >= 100_000_000: return f'{value/100_000_000:.2f} 億'
        if abs(value) >= 10_000: return f'{value/10_000:.2f} 萬'
        return f'{value:.2f}'
    except Exception:
        return str(value)

def fmt_pct(value, already_pct=False):
    if value is None or pd.isna(value): return '—'
    try:
        v = float(value)
        if not already_pct: v *= 100
        return f'{v:.2f}%'
    except Exception:
        return str(value)

def status_badge(status):
    return {'核心觀察':'🔵 核心觀察','持續追蹤':'🟢 持續追蹤','觀察':'🟡 觀察','暫停追蹤':'⚪ 暫停追蹤'}.get(str(status), str(status))

def thinking_questions():
    return [('能力圈','我真的懂這家公司怎麼賺錢嗎？'),('護城河','它的優勢是技術、客戶、成本、法規，還是我想像出來的？'),('安全邊際','如果我錯了，損失能不能承受？'),('反向思考','什麼情況會證明我的投資假設是錯的？'),('第一性原理','這個需求的底層原因是什麼？'),('確認偏誤','我是不是只看支持自己想法的資料？')]
