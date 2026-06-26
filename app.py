import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="PIOS",
    page_icon="📈",
    layout="wide"
)

WATCHLIST_FILE = Path("watchlist.csv")

DEFAULT_DATA = [
    {"ticker": "6969.TW", "name": "成信", "market": "台股", "industry": "環保回收", "theme": "半導體循環經濟", "main_products": "CMP研磨材料回收、功能性陶瓷粉體、電子級二氧化矽", "status": "持續追蹤"},
    {"ticker": "4755.TW", "name": "三福化", "market": "台股", "industry": "半導體化學品", "theme": "半導體材料", "main_products": "電子級化學品、精密化學品", "status": "持續追蹤"},
    {"ticker": "1513.TW", "name": "中興電", "market": "台股", "industry": "電機設備", "theme": "電網升級", "main_products": "重電設備、變電設備、電力工程", "status": "持續追蹤"},
    {"ticker": "8936.TW", "name": "國統", "market": "台股", "industry": "水資源", "theme": "海淡、再生水、管線工程", "main_products": "管線工程、水資源工程、海淡與再生水相關工程", "status": "持續追蹤"},
    {"ticker": "2308.TW", "name": "台達電", "market": "台股", "industry": "電源 / 散熱", "theme": "AI資料中心、能源管理", "main_products": "電源供應器、散熱、工業自動化、能源管理", "status": "持續追蹤"},
    {"ticker": "NVDA", "name": "NVIDIA", "market": "美股", "industry": "半導體", "theme": "AI晶片", "main_products": "GPU、AI加速器、資料中心平台", "status": "持續追蹤"},
    {"ticker": "MSFT", "name": "Microsoft", "market": "美股", "industry": "軟體 / 雲端", "theme": "AI、雲端", "main_products": "Azure、Office、Windows、AI服務", "status": "持續追蹤"},
    {"ticker": "CEG", "name": "Constellation Energy", "market": "美股", "industry": "電力", "theme": "核電、AI資料中心電力", "main_products": "核電、電力供應、能源合約", "status": "持續追蹤"},
    {"ticker": "7203.T", "name": "Toyota", "market": "日股", "industry": "汽車", "theme": "混合動力、自動化", "main_products": "汽車、混合動力車、商用車", "status": "觀察"},
    {"ticker": "8035.T", "name": "Tokyo Electron", "market": "日股", "industry": "半導體設備", "theme": "半導體設備", "main_products": "半導體製造設備、塗佈顯影設備、蝕刻設備", "status": "觀察"},
]


def init_watchlist():
    if not WATCHLIST_FILE.exists():
        pd.DataFrame(DEFAULT_DATA).to_csv(WATCHLIST_FILE, index=False)


def load_watchlist():
    init_watchlist()
    df = pd.read_csv(WATCHLIST_FILE)
    required_columns = ["ticker", "name", "market", "industry", "theme", "main_products", "status"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    return df[required_columns]


def save_watchlist(df):
    df.to_csv(WATCHLIST_FILE, index=False)


def get_status_badge(status):
    if status == "持續追蹤":
        return "🟢 持續追蹤"
    if status == "觀察":
        return "🟡 觀察"
    if status == "暫停追蹤":
        return "⚪ 暫停追蹤"
    return status


def section_title(title, subtitle=None):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


st.title("📈 PIOS")
st.caption("Personal Investment Operating System｜v0.2")
st.divider()

st.sidebar.title("PIOS")
page = st.sidebar.radio(
    "選單",
    ["Dashboard", "Company Center", "Black Swan", "Thinking Models", "Decision Log", "Settings"],
)

watchlist = load_watchlist()

if page == "Dashboard":
    section_title("Today's Focus", "今天最值得你注意的事情")
    st.info("目前沒有需要立即處理的重要事件。")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("台股追蹤", len(watchlist[watchlist["market"] == "台股"]))
    with col2:
        st.metric("美股追蹤", len(watchlist[watchlist["market"] == "美股"]))
    with col3:
        st.metric("日股追蹤", len(watchlist[watchlist["market"] == "日股"]))

    st.divider()
    section_title("Watchlist Overview", "目前追蹤清單")
    display_df = watchlist.copy()
    display_df["status"] = display_df["status"].apply(get_status_badge)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()
    section_title("PIOS Flow", "目前系統核心流程")
    st.markdown("""
**Research → Thinking → Decision → Learning**

- Research：看公司、法說、財報、新聞、重大事件。
- Thinking：用思維模型與反方問題檢查自己的理解。
- Decision：建立投資假設、紀錄決策。
- Learning：回頭檢查自己是判斷正確，還是只是運氣好。
""")

elif page == "Company Center":
    section_title("Company Center", "PIOS 的核心：一家公司一個研究頁")
    col1, col2 = st.columns(2)
    with col1:
        market_filter = st.selectbox("市場篩選", ["全部", "台股", "美股", "日股"])
    with col2:
        status_filter = st.selectbox("狀態篩選", ["全部", "持續追蹤", "觀察", "暫停追蹤"])

    filtered = watchlist.copy()
    if market_filter != "全部":
        filtered = filtered[filtered["market"] == market_filter]
    if status_filter != "全部":
        filtered = filtered[filtered["status"] == status_filter]

    if filtered.empty:
        st.warning("目前沒有符合條件的公司。")
    else:
        selected_ticker = st.selectbox("選擇公司", filtered["ticker"] + "｜" + filtered["name"])
        ticker = selected_ticker.split("｜")[0]
        company = watchlist[watchlist["ticker"] == ticker].iloc[0]

        st.divider()
        st.markdown(f"# {company['name']} ({company['ticker']})")
        st.caption(get_status_badge(company["status"]))
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### 基本資料")
            st.write(f"**市場：** {company['market']}")
            st.write(f"**產業：** {company['industry']}")
            st.write(f"**題材：** {company['theme']}")
        with col_b:
            st.markdown("### 主要產品 / 方向")
            st.write(company["main_products"])

        st.divider()
        st.markdown("## Research")
        st.markdown("""這裡之後會放：公司介紹、財報、法說會、新聞、重大事件。""")
        st.markdown("## Thinking")
        st.markdown("""這裡之後會放：思維模型評分、護城河、第一性原理、反方問題、蘇格拉底式反問。""")
        st.markdown("## Decision")
        st.markdown("""這裡之後會放：Investment Thesis、Decision Log、Confidence、Checklist。""")
        st.markdown("## Learning")
        st.markdown("""這裡之後會放：投資日誌、決策回放、偏誤分析、經驗整理。""")

    st.divider()
    section_title("新增公司")
    with st.form("add_company"):
        ticker = st.text_input("股票代號", placeholder="例如：6969.TW / NVDA / 7203.T")
        name = st.text_input("公司名稱", placeholder="例如：成信")
        market = st.selectbox("市場", ["台股", "美股", "日股"])
        industry = st.text_input("產業", placeholder="例如：環保回收")
        theme = st.text_input("題材 / 主要方向", placeholder="例如：半導體循環經濟")
        main_products = st.text_area("主要產品 / 公司方向", placeholder="例如：CMP研磨材料回收、功能性陶瓷粉體、電子級二氧化矽")
        status = st.selectbox("狀態", ["持續追蹤", "觀察", "暫停追蹤"])
        submitted = st.form_submit_button("新增公司")
        if submitted:
            if not ticker or not name:
                st.error("股票代號與公司名稱必填。")
            else:
                new_row = pd.DataFrame([{"ticker": ticker.strip(), "name": name.strip(), "market": market, "industry": industry.strip(), "theme": theme.strip(), "main_products": main_products.strip(), "status": status}])
                watchlist = pd.concat([watchlist, new_row], ignore_index=True)
                watchlist = watchlist.drop_duplicates(subset=["ticker"], keep="last")
                save_watchlist(watchlist)
                st.success(f"已新增 / 更新：{ticker} {name}")
                st.rerun()

    st.divider()
    section_title("刪除公司")
    delete_ticker = st.selectbox("選擇要刪除的股票", [""] + watchlist["ticker"].astype(str).tolist())
    if st.button("刪除公司"):
        if delete_ticker:
            watchlist = watchlist[watchlist["ticker"] != delete_ticker]
            save_watchlist(watchlist)
            st.success(f"已刪除：{delete_ticker}")
            st.rerun()
        else:
            st.warning("請先選擇要刪除的股票。")

elif page == "Black Swan":
    section_title("Black Swan Center", "劇烈波動提醒中心")
    st.warning("目前是 v0.2 佔位版本，尚未接入即時股價。")
    st.markdown("""
未來這裡會檢查：

- 單日大漲 / 大跌
- 三日急漲 / 急跌
- 成交量放大
- 距 52 週高點跌深
- 放量站回均線
- 新聞熱度暴增

只有劇烈異動才 Telegram 推播。
""")
    st.dataframe(watchlist, use_container_width=True, hide_index=True)

elif page == "Thinking Models":
    section_title("Thinking Models", "用來反問自己的投資思考工具")
    models = [
        {"model": "能力圈", "question": "我真的懂這家公司怎麼賺錢嗎？"},
        {"model": "護城河", "question": "它的優勢是技術、客戶、成本、法規，還是我想像出來的？"},
        {"model": "安全邊際", "question": "如果我錯了，損失能不能承受？"},
        {"model": "反向思考", "question": "什麼情況會證明我的投資假設是錯的？"},
        {"model": "第一性原理", "question": "這個需求的底層原因是什麼？"},
        {"model": "確認偏誤", "question": "我是不是只看支持自己想法的資料？"},
    ]
    st.dataframe(pd.DataFrame(models), use_container_width=True, hide_index=True)

elif page == "Decision Log":
    section_title("Decision Log", "先記錄，再檢討")
    st.info("v0.2 先建立概念，之後會加入儲存功能。")
    with st.form("decision_log"):
        company = st.text_input("公司 / 股票")
        action = st.selectbox("動作", ["研究", "觀察", "買進", "加碼", "減碼", "賣出", "放棄"])
        reason = st.text_area("原因")
        risk = st.text_area("主要風險")
        thesis = st.text_area("投資假設")
        submitted = st.form_submit_button("暫時送出")
        if submitted:
            st.success("已收到。v0.3 會加入正式儲存功能。")
            st.write("公司：", company)
            st.write("動作：", action)
            st.write("原因：", reason)
            st.write("風險：", risk)
            st.write("投資假設：", thesis)

elif page == "Settings":
    section_title("Settings", "系統設定")
    st.markdown("""
目前版本：**PIOS v0.2**

下一版預計加入：

- yfinance 股價資料
- 黑天鵝分數
- Telegram 推播設定
- Decision Log 儲存
""")
