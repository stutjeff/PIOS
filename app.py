from datetime import datetime
import pandas as pd
import streamlit as st
from pathlib import Path
from core.watchlist import load_watchlist, save_watchlist, normalize_ticker
from core.scoring import black_swan_score, grade
from core.ui import section, fmt_num, fmt_pct, status_badge, questions
from data_sources.yfinance_source import get_price_data, get_info
from data_sources.biggo_source import get_biggo_overview, get_biggo_financial
st.set_page_config(page_title='PIOS', page_icon='📈', layout='wide')
DATA=Path('data'); DATA.mkdir(exist_ok=True)
def load_table(name, cols):
    p=DATA/name
    if not p.exists(): pd.DataFrame(columns=cols).to_csv(p,index=False)
    df=pd.read_csv(p)
    for c in cols:
        if c not in df.columns: df[c]=''
    return df[cols]
def save_table(name, df): df.to_csv(DATA/name,index=False)
NOTES=['ticker','note','updated_at']; THESIS=['ticker','thesis','risk','sell_condition','confidence','updated_at']; DEC=['date','ticker','action','reason','risk','thesis']
st.title('📈 PIOS'); st.caption('Personal Investment Operating System｜v2.0 Architecture + BigGo Layer')
watchlist=load_watchlist(); notes=load_table('company_notes.csv',NOTES); thesis_df=load_table('investment_thesis.csv',THESIS); decision=load_table('decision_log.csv',DEC)
st.sidebar.title('PIOS'); page=st.sidebar.radio('選單',['Dashboard','Company Center','Watchlist','Black Swan','Settings'])
if page=='Dashboard':
    section('Today\'s Focus','今天最值得你注意的事情'); st.info('目前沒有需要立即處理的重要事件。')
    c1,c2,c3,c4=st.columns(4); c1.metric('台股',len(watchlist[watchlist.market=='台股'])); c2.metric('美股',len(watchlist[watchlist.market=='美股'])); c3.metric('日股',len(watchlist[watchlist.market=='日股'])); c4.metric('公司總數',len(watchlist))
    show=watchlist[['ticker','name','market','industry','theme','status']].copy(); show['status']=show.status.apply(status_badge); st.dataframe(show,use_container_width=True,hide_index=True)
elif page=='Company Center':
    section('Company Center','公司研究中心')
    selected=st.sidebar.radio('公司',(watchlist.ticker+'｜'+watchlist.name).tolist())
    ticker=selected.split('｜')[0]; company=watchlist[watchlist.ticker==ticker].iloc[0]
    price=get_price_data(ticker); info=get_info(ticker); biggo=get_biggo_overview(ticker); biggo_fin=get_biggo_financial(ticker); swan,rs=black_swan_score(price)
    st.markdown(f"# {company['name']} ({ticker})"); st.caption(f"{status_badge(company['status'])}｜{company['market']}｜{company['industry']}｜{company['sub_industry']}")
    a,b,c,d=st.columns(4)
    if price: a.metric('收盤價',f"{price['price']:.2f}",f"{price['daily_change']:+.2f}%"); b.metric('52週高點回落',fmt_pct(price['drop_from_high'],True)); c.metric('量能倍率',f"{price['volume_ratio']:.2f}x")
    else: a.metric('收盤價','—'); b.metric('52週高點回落','—'); c.metric('量能倍率','—')
    d.metric('黑天鵝分數',swan,grade(swan))
    tabs=st.tabs(['公司','估值','BigGo','黑天鵝','思維模型','Thesis / 筆記','Decision Log'])
    with tabs[0]:
        section('公司概況'); st.write(f"**主要題材：** {company['theme']}"); st.write(f"**主要產品：** {company['main_products']}"); st.write(f"**商業模式：** {company['business_model']}"); st.write(f"**護城河：** {company['moat']}"); st.info(f"關鍵問題：{company['key_questions']}")
    with tabs[1]:
        section('估值 / 基本面','yfinance 為備援資料源'); x,y,z=st.columns(3); x.metric('市值',fmt_num(info.get('market_cap'))); y.metric('PE',fmt_num(info.get('pe'))); z.metric('PB',fmt_num(info.get('pb'))); st.write('殖利率：',fmt_pct(info.get('dividend_yield')),'ROE：',fmt_pct(info.get('roe')))
    with tabs[2]:
        section('BigGo Data Source','PoC：先測穩定性，再決定是否正式替換'); st.subheader('概覽頁'); st.dataframe(pd.DataFrame([biggo]),use_container_width=True,hide_index=True); st.subheader('財報頁'); st.dataframe(pd.DataFrame([biggo_fin]),use_container_width=True,hide_index=True)
    with tabs[3]:
        section('黑天鵝分析'); st.metric('黑天鵝分數',swan,grade(swan)); [st.write('- '+r) for r in rs]
    with tabs[4]:
        section('思維模型反問'); scores=[]
        for m,q in questions():
            with st.expander(m): st.write(q); scores.append(st.slider('分數',0,100,70,key=f'{ticker}_{m}'))
        st.metric('思維模型總分',round(sum(scores)/len(scores)),grade(round(sum(scores)/len(scores))))
    with tabs[5]:
        section('Investment Thesis'); cur=thesis_df[thesis_df.ticker==ticker]
        if not cur.empty: st.dataframe(cur,use_container_width=True,hide_index=True)
        with st.form(f'thesis_{ticker}'):
            th=st.text_area('我為什麼看好 / 追蹤？'); risk=st.text_area('最大風險'); sell=st.text_area('什麼情況會賣出 / 放棄？'); conf=st.slider('信心',0,100,70); ok=st.form_submit_button('儲存 Thesis')
            if ok: thesis_df=pd.concat([thesis_df,pd.DataFrame([{'ticker':ticker,'thesis':th,'risk':risk,'sell_condition':sell,'confidence':conf,'updated_at':datetime.now().strftime('%Y-%m-%d %H:%M')}])],ignore_index=True); save_table('investment_thesis.csv',thesis_df); st.rerun()
    with tabs[6]: st.dataframe(decision[decision.ticker==ticker],use_container_width=True,hide_index=True)
elif page=='Watchlist':
    section('Watchlist 管理'); st.dataframe(watchlist,use_container_width=True,hide_index=True)
    with st.form('add'):
        t=st.text_input('股票代號'); name=st.text_input('公司名稱'); market=st.selectbox('市場',['台股','美股','日股']); status=st.selectbox('狀態',['核心觀察','持續追蹤','觀察','暫停追蹤']); industry=st.text_input('產業'); sub=st.text_input('次產業'); theme=st.text_input('題材'); prod=st.text_area('主要產品'); bm=st.text_area('商業模式'); ok=st.form_submit_button('新增 / 更新')
        if ok:
            row={c:'' for c in watchlist.columns}; row.update({'ticker':normalize_ticker(t,market),'name':name,'market':market,'status':status,'industry':industry,'sub_industry':sub,'theme':theme,'main_products':prod,'business_model':bm})
            watchlist=pd.concat([watchlist,pd.DataFrame([row])],ignore_index=True).drop_duplicates('ticker',keep='last'); save_watchlist(watchlist); st.rerun()
elif page=='Black Swan':
    rows=[]
    for _,r in watchlist.iterrows():
        s,rr=black_swan_score(get_price_data(r.ticker)); rows.append({'ticker':r.ticker,'name':r.name,'score':s,'reason':'；'.join(rr)})
    st.dataframe(pd.DataFrame(rows).sort_values('score',ascending=False),use_container_width=True,hide_index=True)
elif page=='Settings':
    section('Settings'); st.markdown('目前版本：**PIOS v2.0 Architecture + BigGo Layer**')
