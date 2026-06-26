import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="PIOS",
    page_icon="📈",
    layout="wide"
)

WATCHLIST_FILE = Path("watchlist.csv")


def load_watchlist():
    if WATCHLIST_FILE.exists():
        return pd.read_csv(WATCHLIST_FILE)
    return pd.DataFrame(columns=["ticker", "name", "market", "industry", "theme", "status"])


def save_watchlist(df):
    df.to_csv(WATCHLIST_FILE, index=False)


st.title("📈 PIOS")
st.subheader("Personal Investment Operating System")

st.divider()

st.header("Today's Focus")
st.info("目前沒有需要立即處理的重要事件。")

st.divider()

st.header("Company Center")

watchlist = load_watchlist()

market_filter = st.selectbox("市場篩選", ["全部", "台股", "美股", "日股"])

filtered = watchlist.copy()
if market_filter != "全部":
    filtered = filtered[filtered["market"] == market_filter]

st.dataframe(filtered, use_container_width=True, hide_index=True)

st.divider()

st.header("新增公司")

with st.form("add_company"):
    ticker = st.text_input("股票代號", placeholder="例如：6969.TW / NVDA / 7203.T")
    name = st.text_input("公司名稱", placeholder="例如：成信")
    market = st.selectbox("市場", ["台股", "美股", "日股"])
    industry = st.text_input("產業", placeholder="例如：環保回收")
    theme = st.text_input("題材 / 主要方向", placeholder="例如：半導體循環經濟")
    status = st.selectbox("狀態", ["持續追蹤", "觀察", "暫停追蹤"])
    submitted = st.form_submit_button("新增")

    if submitted:
        if not ticker or not name:
            st.error("股票代號與公司名稱必填。")
        else:
            new_row = pd.DataFrame([{
                "ticker": ticker.strip(),
                "name": name.strip(),
                "market": market,
                "industry": industry.strip(),
                "theme": theme.strip(),
                "status": status
            }])
            watchlist = pd.concat([watchlist, new_row], ignore_index=True)
            watchlist = watchlist.drop_duplicates(subset=["ticker"], keep="last")
            save_watchlist(watchlist)
            st.success(f"已新增：{ticker} {name}")
            st.rerun()

st.divider()

st.header("刪除公司")

delete_ticker = st.selectbox(
    "選擇要刪除的股票",
    [""] + watchlist["ticker"].astype(str).tolist()
)

if st.button("刪除"):
    if delete_ticker:
        watchlist = watchlist[watchlist["ticker"] != delete_ticker]
        save_watchlist(watchlist)
        st.success(f"已刪除：{delete_ticker}")
        st.rerun()

st.divider()

st.header("Research")
col1, col2 = st.columns(2)

with col1:
    st.button("🏢 Company")
    st.button("📊 Financial Report")
    st.button("🎤 Conference Call")

with col2:
    st.button("📰 News")
    st.button("🦢 Black Swan")
    st.button("🧠 Thinking Models")

st.divider()

st.header("Decision")
st.button("📖 Investment Thesis")
st.button("📝 Decision Log")

st.divider()

st.header("Learning")
st.button("📚 Journal")
st.button("🔁 Replay")

st.divider()
st.caption("PIOS v0.1 — Build first, improve later.")
