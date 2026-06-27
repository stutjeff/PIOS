from datetime import datetime
import pandas as pd
import streamlit as st
from core.watchlist import load_watchlist, save_watchlist, normalize_ticker
from core.storage import load_csv, save_csv
from core.scoring import black_swan_score, grade
from core.ui import section, fmt_num, fmt_pct, status_badge, thinking_questions
from data_sources.yfinance_source import get_price_data, get_info
from data_sources.biggo_source import get_biggo_overview, get_biggo_financial
from data_sources.health import run_health_check

st.set_page_config(page_title='PIOS', page_icon='📈', layout='wide')
NOTES_COLS=['ticker','note','updated_at']
THESIS_COLS=['ticker','thesis','risk','sell_condition','confidence','updated_at']
DECISION_COLS=['date','ticker','action','reason','risk','thesis']

st.title('📈 PIOS')
st.caption('Personal Investment Operating System｜v2.1 Data Source Health Check')
watchlist=load_watchlist()
notes_df=load_csv('company_notes.csv', NOTES_COLS)
thesis_df=load_csv('investment_thesis.csv', THESIS_COLS)
decision_df=load_csv('decision_log.csv', DECISION_COLS)

st.sidebar.title('PIOS')
page=st.sidebar.radio('選單',['Dashboard','Company Center','Watchlist','Data Health','Black Swan','Settings'])

if page=='Dashboard':
    section('Today\'s Focus','今天最值得你注意的事情')
    st.info('目前沒有需要立即處理的重要事件。')
    c1,c2,c3,c4=st.columns(4)
    c1.metric('台股',len(watchlist[watchlist['market']=='台股']))
    c2.metric('美股',len(watchlist[watchlist['market']=='美股']))
    c3.metric('日股',len(watchlist[watchlist['market']=='日股']))
    c4.metric('公司總數',len(watchlist))
    st.divider()
    show=watchlist[['ticker','name','market','industry','theme','status']].copy()
    show['status']=show['status'].apply(status_badge)
    st.dataframe(show,use_container_width=True,hide_index=True)

elif page=='Company Center':
    section('Company Center','公司研究中心')
    market_filter=st.sidebar.selectbox('市場篩選',['全部','台股','美股','日股'])
    filtered=watchlist.copy()
    if market_filter!='全部': filtered=filtered[filtered['market']==market_filter]
    if filtered.empty:
        st.warning('沒有公司'); st.stop()
    selected=st.sidebar.radio('公司',(filtered['ticker']+'｜'+filtered['name']).tolist())
    ticker=selected.split('｜')[0]
    company=watchlist[watchlist['ticker']==ticker].iloc[0]
    price=get_price_data(ticker); yinfo=get_info(ticker)
    biggo=get_biggo_overview(ticker); biggo_fin=get_biggo_financial(ticker)
    swan,reasons=black_swan_score(price)
    st.markdown(f"# {company['name']} ({ticker})")
    st.caption(f"{status_badge(company['status'])}｜{company['market']}｜{company['industry']}｜{company['sub_industry']}")
    k1,k2,k3,k4=st.columns(4)
    if price:
        k1.metric('收盤價',f"{price['price']:.2f}",f"{price['daily_change']:+.2f}%")
        k2.metric('52週高點回落',fmt_pct(price['drop_from_high'],already_pct=True))
        k3.metric('量能倍率',f"{price['volume_ratio']:.2f}x")
    else:
        k1.metric('收盤價','—'); k2.metric('52週高點回落','—'); k3.metric('量能倍率','—')
    k4.metric('黑天鵝分數',swan,grade(swan))
    tabs=st.tabs(['公司','估值','BigGo','黑天鵝','思維模型','Thesis / 筆記','Decision Log'])
    with tabs[0]:
        section('公司概況')
        st.write(f"**主要題材：** {company['theme']}")
        st.write(f"**主要產品：** {company['main_products']}")
        st.write(f"**商業模式：** {company['business_model']}")
        st.write(f"**護城河：** {company['moat']}")
        st.info(f"關鍵問題：{company['key_questions']}")
    with tabs[1]:
        section('估值 / 基本面','yfinance 為備援資料源')
        c1,c2,c3=st.columns(3)
        c1.metric('市值',fmt_num(yinfo.get('market_cap'))); c2.metric('PE',fmt_num(yinfo.get('pe'))); c3.metric('PB',fmt_num(yinfo.get('pb')))
        st.caption(f"殖利率：{fmt_pct(yinfo.get('dividend_yield'))} ROE：{fmt_pct(yinfo.get('roe'))}")
    with tabs[2]:
        section('BigGo Data Source','目前只是 PoC；若失敗，不影響主系統')
        st.subheader('概覽頁'); st.dataframe(pd.DataFrame([biggo]),use_container_width=True,hide_index=True)
        st.subheader('財報頁'); st.dataframe(pd.DataFrame([biggo_fin]),use_container_width=True,hide_index=True)
    with tabs[3]:
        section('黑天鵝分析'); st.metric('黑天鵝分數',swan,grade(swan))
        for r in reasons: st.write(f'- {r}')
    with tabs[4]:
        section('思維模型反問'); scores=[]
        for model,q in thinking_questions():
            with st.expander(model):
                st.write(q); s=st.slider('分數',0,100,70,key=f'{ticker}_{model}_score'); scores.append(s)
        total=round(sum(scores)/len(scores)) if scores else 0
        st.metric('思維模型總分',total,grade(total))
    with tabs[5]:
        section('Investment Thesis')
        cur=thesis_df[thesis_df['ticker']==ticker]
        if not cur.empty: st.dataframe(cur,use_container_width=True,hide_index=True)
        with st.form(f'thesis_{ticker}'):
            thesis=st.text_area('我為什麼看好 / 追蹤？'); risk=st.text_area('最大風險'); sell=st.text_area('什麼情況會賣出 / 放棄？'); conf=st.slider('信心',0,100,70)
            ok=st.form_submit_button('儲存 Thesis')
            if ok:
                row=pd.DataFrame([{'ticker':ticker,'thesis':thesis,'risk':risk,'sell_condition':sell,'confidence':conf,'updated_at':datetime.now().strftime('%Y-%m-%d %H:%M')}])
                thesis_df=pd.concat([thesis_df,row],ignore_index=True); save_csv('investment_thesis.csv',thesis_df); st.success('已儲存 Thesis'); st.rerun()
    with tabs[6]:
        section('Decision Log'); cur=decision_df[decision_df['ticker']==ticker]; st.dataframe(cur,use_container_width=True,hide_index=True)

elif page=='Watchlist':
    section('Watchlist 管理')
    show=watchlist[['ticker','name','market','industry','theme','status']].copy(); show['status']=show['status'].apply(status_badge)
    st.dataframe(show,use_container_width=True,hide_index=True)
    with st.form('add_company'):
        ticker_raw=st.text_input('股票代號',placeholder='6641.tw / NVDA / 7203.t'); name=st.text_input('公司名稱'); market=st.selectbox('市場',['台股','美股','日股']); status=st.selectbox('狀態',['核心觀察','持續追蹤','觀察','暫停追蹤'])
        industry=st.text_input('產業'); sub_industry=st.text_input('次產業'); theme=st.text_input('題材'); main_products=st.text_area('主要產品'); business_model=st.text_area('商業模式'); customers=st.text_area('主要客戶'); suppliers=st.text_area('主要供應商'); competitors=st.text_area('競爭對手'); moat=st.text_area('護城河摘要'); management=st.text_area('管理層'); key_questions=st.text_area('關鍵問題')
        ok=st.form_submit_button('新增 / 更新公司')
        if ok:
            ticker=normalize_ticker(ticker_raw,market)
            row=pd.DataFrame([{'ticker':ticker,'name':name,'market':market,'industry':industry,'sub_industry':sub_industry,'theme':theme,'main_products':main_products,'business_model':business_model,'customers':customers,'suppliers':suppliers,'competitors':competitors,'moat':moat,'management':management,'key_questions':key_questions,'status':status}])
            watchlist=pd.concat([watchlist,row],ignore_index=True).drop_duplicates('ticker',keep='last'); save_watchlist(watchlist); st.success(f'已新增 / 更新：{ticker}'); st.rerun()

elif page=='Data Health':
    section('Data Source Health Check','先測資料源穩定性，不急著接到正式研究頁')
    stock_id=st.text_input('台股代號',value='2330'); yf_ticker=st.text_input('yfinance 代號',value=f'{stock_id}.TW'); biggo_ticker=st.text_input('BigGo 代號',value=f'{stock_id}.TW')
    st.warning('這頁是壓力測試。失敗不是壞事，是在幫我們找出誰不能當地基。')
    if st.button('開始測試'):
        with st.spinner('正在測試各資料源...'):
            df=run_health_check(stock_id=stock_id,yf_ticker=yf_ticker,biggo_ticker=biggo_ticker)
        st.dataframe(df,use_container_width=True,hide_index=True)
        ok_count=int((df['status']=='✅ 成功').sum())
        st.metric('成功來源數',ok_count,f'{ok_count}/{len(df)}')

elif page=='Black Swan':
    section('Black Swan Center'); rows=[]
    for _,row in watchlist.iterrows():
        p=get_price_data(row['ticker']); s,rs=black_swan_score(p)
        rows.append({'ticker':row['ticker'],'name':row['name'],'market':row['market'],'score':s,'reason':'；'.join(rs)})
    st.dataframe(pd.DataFrame(rows).sort_values('score',ascending=False),use_container_width=True,hide_index=True)

elif page=='Settings':
    section('Settings')
    st.markdown('''目前版本：**PIOS v2.1 Data Source Health Check**

本版重點：
- 新增 Data Health 頁
- 測 TWSE OpenAPI
- 測 TWSE 個股日成交
- 測 FinMind
- 測 yfinance
- 測 BigGo
''')
