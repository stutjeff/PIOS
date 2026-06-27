import streamlit as st
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="PIOS", page_icon="📈", layout="wide")

WATCHLIST_FILE = Path("watchlist.csv")
NOTES_FILE = Path("company_notes.csv")
THESIS_FILE = Path("investment_thesis.csv")
DECISION_FILE = Path("decision_log.csv")

REQUIRED_COLUMNS = [
    "ticker", "name", "market", "industry", "sub_industry", "theme",
    "main_products", "business_model", "customers", "competitors", "key_questions", "status"
]

DEFAULT_DATA = [
    ["6969.TW", "成信", "台股", "環保回收", "半導體循環經濟", "半導體、循環經濟、零廢製造", "CMP研磨材料回收、功能性陶瓷粉體、電子級二氧化矽", "承接半導體相關廢棄物與副產物，透過回收、純化與再利用技術轉為可銷售材料。", "台積電供應鏈、日月光供應鏈、半導體與電子材料客戶", "其他環保處理商、半導體廢棄物回收商、材料再生業者", "中科處理額度是否放寬？球形二氧化矽驗證是否完成？南科零廢中心是否落地？", "持續追蹤"],
    ["4755.TW", "三福化", "台股", "半導體化學品", "電子級化學品", "半導體材料、特用化學", "電子級化學品、精密化學品、特用材料", "提供半導體與電子產業所需化學材料。", "半導體、面板、電子材料客戶", "國內外電子級化學品供應商", "先進製程需求是否擴大？毛利率是否改善？新客戶驗證是否進展？", "持續追蹤"],
    ["1513.TW", "中興電", "台股", "電機設備", "重電 / 電網", "電網升級、AI電力、能源轉型", "重電設備、變電設備、電力工程、智慧電網相關設備", "提供電力基礎建設設備與工程服務，受惠電網升級與用電需求增加。", "台電、公共工程、民間電力建設客戶", "華城、士電、國際重電設備商", "訂單能見度是否延續？毛利率是否維持？AI電力需求是否實際反映？", "持續追蹤"],
    ["8936.TW", "國統", "台股", "水資源", "管線 / 海淡 / 再生水", "水資源、海淡、極端氣候", "管線工程、水資源工程、海淡與再生水相關工程", "承接大型管線、水資源與海淡再生水工程，受惠水資源基礎建設。", "政府標案、公用事業、工業用水需求者", "水資源工程承包商、管線工程公司", "海淡與再生水標案是否增加？工程毛利率是否改善？營運權是否擴大？", "持續追蹤"],
    ["2308.TW", "台達電", "台股", "電源 / 散熱", "AI資料中心 / 能源管理", "AI資料中心、電源、液冷、能源管理", "電源供應器、散熱、工業自動化、能源管理、資料中心解決方案", "提供高效率電源、散熱與能源管理方案，受惠AI資料中心與電氣化趨勢。", "資料中心、伺服器、工業自動化、電動車與能源客戶", "Vertiv、Schneider Electric、其他電源與散熱供應商", "AI資料中心需求是否持續？液冷與電源產品毛利率如何？估值是否過熱？", "持續追蹤"],
    ["NVDA", "NVIDIA", "美股", "半導體", "AI晶片", "AI、GPU、資料中心", "GPU、AI加速器、資料中心平台、CUDA生態系", "銷售AI晶片、資料中心平台與軟硬整合解決方案。", "雲端服務商、AI模型公司、企業資料中心", "AMD、Broadcom、ASIC供應商、雲端自研晶片", "AI資本支出是否維持？毛利率是否下滑？競爭者ASIC是否侵蝕需求？", "持續追蹤"],
    ["MSFT", "Microsoft", "美股", "軟體 / 雲端", "AI雲端", "AI、雲端、企業軟體", "Azure、Office、Windows、Copilot、企業雲端服務", "以雲端、訂閱制軟體與企業服務創造穩定現金流。", "企業、政府、個人用戶、開發者", "Google、Amazon、Oracle、Salesforce", "AI投入是否轉化為收入？Azure成長是否延續？資本支出壓力是否上升？", "持續追蹤"],
    ["CEG", "Constellation Energy", "美股", "電力", "核電 / 資料中心電力", "核電、AI資料中心電力、長約供電", "核電、電力供應、能源合約", "提供穩定低碳電力，受惠資料中心長期用電需求。", "公用事業、企業客戶、資料中心", "其他電力公司、再生能源供應商、天然氣發電商", "AI資料中心長約是否增加？核電政策是否支持？電價與資本支出如何變化？", "持續追蹤"],
    ["7203.T", "Toyota", "日股", "汽車", "混合動力 / 自動化", "混合動力、全球汽車、自動化", "汽車、混合動力車、商用車", "全球汽車製造與銷售，混合動力與供應鏈管理為重要優勢。", "全球汽車消費者、商用車客戶", "Volkswagen、Hyundai、Tesla、中國車企", "混合動力優勢是否延續？電動車轉型是否落後？匯率是否影響獲利？", "觀察"],
    ["8035.T", "Tokyo Electron", "日股", "半導體設備", "前段製程設備", "半導體設備、先進製程", "半導體製造設備、塗佈顯影設備、蝕刻設備", "銷售半導體製造設備，受惠晶圓廠資本支出。", "晶圓代工、記憶體、IDM半導體公司", "ASML、Applied Materials、Lam Research", "半導體資本支出是否回升？中國限制是否影響？先進製程需求是否延續？", "觀察"],
]

def init_csv(path, columns):
    if not path.exists():
        pd.DataFrame(columns=columns).to_csv(path, index=False)

def init_watchlist():
    if not WATCHLIST_FILE.exists():
        pd.DataFrame(DEFAULT_DATA, columns=REQUIRED_COLUMNS).to_csv(WATCHLIST_FILE, index=False)

def load_watchlist():
    init_watchlist()
    df = pd.read_csv(WATCHLIST_FILE)
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[REQUIRED_COLUMNS]

def save_watchlist(df):
    df.to_csv(WATCHLIST_FILE, index=False)

def load_notes():
    init_csv(NOTES_FILE, ["ticker", "note", "updated_at"])
    return pd.read_csv(NOTES_FILE)

def save_notes(df):
    df.to_csv(NOTES_FILE, index=False)

def load_thesis():
    init_csv(THESIS_FILE, ["ticker", "thesis", "risk", "check_item", "updated_at"])
    return pd.read_csv(THESIS_FILE)

def save_thesis(df):
    df.to_csv(THESIS_FILE, index=False)

def load_decisions():
    init_csv(DECISION_FILE, ["date", "ticker", "action", "reason", "risk", "thesis"])
    return pd.read_csv(DECISION_FILE)

def save_decisions(df):
    df.to_csv(DECISION_FILE, index=False)

@st.cache_data(ttl=900)
def get_price_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
        if data.empty or len(data) < 5:
            return None
        close = data["Close"]
        volume = data["Volume"]
        latest_close = float(close.iloc[-1])
        prev_close = float(close.iloc[-2])
        daily_change = (latest_close / prev_close - 1) * 100
        high_52w = float(close.max())
        drop_from_high = (latest_close / high_52w - 1) * 100
        avg_volume_20 = float(volume.tail(20).mean())
        latest_volume = float(volume.iloc[-1])
        volume_ratio = latest_volume / avg_volume_20 if avg_volume_20 > 0 else 0
        return {"price": latest_close, "daily_change": daily_change, "drop_from_high": drop_from_high, "volume_ratio": volume_ratio}
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            "market_cap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
        }
    except Exception:
        return {}

def fmt_num(value):
    if value is None or pd.isna(value):
        return "—"
    try:
        value = float(value)
        if abs(value) >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:.2f} 兆"
        if abs(value) >= 100_000_000:
            return f"{value / 100_000_000:.2f} 億"
        if abs(value) >= 10_000:
            return f"{value / 10_000:.2f} 萬"
        return f"{value:.2f}"
    except Exception:
        return "—"

def fmt_pct(value):
    if value is None or pd.isna(value):
        return "—"
    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return "—"

def get_status_badge(status):
    if status == "持續追蹤": return "🟢 持續追蹤"
    if status == "觀察": return "🟡 觀察"
    if status == "暫停追蹤": return "⚪ 暫停追蹤"
    return str(status)

def black_swan_score(price_data):
    if not price_data:
        return 0, ["尚未取得股價資料"]
    score = 0
    reasons = []
    if abs(price_data["daily_change"]) >= 7:
        score += 25
        reasons.append("單日漲跌超過 7%")
    if price_data["volume_ratio"] >= 2:
        score += 20
        reasons.append("成交量超過 20 日均量 2 倍")
    if price_data["drop_from_high"] <= -30:
        score += 15
        reasons.append("距 52 週高點跌深超過 30%")
    if price_data["drop_from_high"] <= -50:
        score += 15
        reasons.append("距 52 週高點跌深超過 50%")
    if not reasons:
        reasons.append("目前沒有明顯黑天鵝異動")
    return score, reasons

def thinking_questions():
    return [
        ("能力圈", "我真的懂這家公司怎麼賺錢嗎？"),
        ("護城河", "它的優勢是技術、客戶、成本、法規，還是我想像出來的？"),
        ("安全邊際", "如果我錯了，損失能不能承受？"),
        ("反向思考", "什麼情況會證明我的投資假設是錯的？"),
        ("第一性原理", "這個需求的底層原因是什麼？"),
        ("確認偏誤", "我是不是只看支持自己想法的資料？"),
    ]

def section(title, desc=None):
    st.markdown(f"## {title}")
    if desc:
        st.caption(desc)

st.title("📈 PIOS")
st.caption("Personal Investment Operating System｜v1.0 Company Center")

watchlist = load_watchlist()
notes = load_notes()
thesis_df = load_thesis()
decision_df = load_decisions()

st.sidebar.title("PIOS")
page = st.sidebar.radio("選單", ["Dashboard", "Company Center", "Black Swan", "Thinking Models", "Decision Log", "Settings"])

if page == "Dashboard":
    section("Today's Focus", "今天最值得你注意的事情")
    st.info("目前沒有需要立即處理的重要事件。")
    c1, c2, c3 = st.columns(3)
    c1.metric("台股追蹤", len(watchlist[watchlist["market"] == "台股"]))
    c2.metric("美股追蹤", len(watchlist[watchlist["market"] == "美股"]))
    c3.metric("日股追蹤", len(watchlist[watchlist["market"] == "日股"]))
    st.divider()
    section("Watchlist Overview", "目前追蹤清單")
    show = watchlist[["ticker", "name", "market", "industry", "theme", "status"]].copy()
    show["status"] = show["status"].apply(get_status_badge)
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.divider()
    section("PIOS Flow", "目前系統核心流程")
    st.markdown("""
    **Research → Thinking → Decision → Learning**

    - Research：看公司、法說、財報、新聞、重大事件。
    - Thinking：用思維模型與反方問題檢查自己的理解。
    - Decision：建立投資假設、紀錄決策。
    - Learning：回頭檢查自己是判斷正確，還是只是運氣好。
    """)

elif page == "Company Center":
    section("Company Center", "一家公司一個研究頁")
    col1, col2 = st.columns(2)
    with col1:
        market_filter = st.selectbox("市場篩選", ["全部", "台股", "美股", "日股"])
    with col2:
        status_filter = st.selectbox("狀態篩選", ["全部", "持續追蹤", "觀察", "暫停追蹤"])

    filtered = watchlist.copy()
    if market_filter != "全部": filtered = filtered[filtered["market"] == market_filter]
    if status_filter != "全部": filtered = filtered[filtered["status"] == status_filter]

    if filtered.empty:
        st.warning("目前沒有符合條件的公司。")
    else:
        selected = st.selectbox("選擇公司", filtered["ticker"] + "｜" + filtered["name"])
        ticker = selected.split("｜")[0]
        company = watchlist[watchlist["ticker"] == ticker].iloc[0]
        price = get_price_data(ticker)
        info = get_info(ticker)
        swan_score, swan_reasons = black_swan_score(price)

        st.divider()
        st.markdown(f"# {company['name']} ({company['ticker']})")
        st.caption(f"{get_status_badge(company['status'])}｜{company['market']}｜{company['industry']}｜{company['sub_industry']}")

        c1, c2, c3, c4 = st.columns(4)
        if price:
            c1.metric("收盤價", f"{price['price']:.2f}", f"{price['daily_change']:+.2f}%")
            c2.metric("距52週高點", f"{price['drop_from_high']:.2f}%")
            c3.metric("量能倍率", f"{price['volume_ratio']:.2f}x")
        else:
            c1.metric("收盤價", "—")
            c2.metric("距52週高點", "—")
            c3.metric("量能倍率", "—")
        c4.metric("黑天鵝分數", swan_score)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["公司", "估值", "黑天鵝", "思維模型", "Thesis / 筆記", "Decision Log"])
        with tab1:
            section("公司基本資料")
            st.write(f"**主要題材：** {company['theme']}")
            st.write(f"**主要產品 / 方向：** {company['main_products']}")
            st.write(f"**商業模式：** {company['business_model']}")
            st.write(f"**主要客戶：** {company['customers']}")
            st.write(f"**競爭對手：** {company['competitors']}")
            st.write(f"**關鍵問題：** {company['key_questions']}")
        with tab2:
            section("估值 / 基本面", "資料來源：yfinance，部分台股資料可能不完整")
            v1, v2, v3 = st.columns(3)
            v1.metric("市值", fmt_num(info.get("market_cap")))
            v2.metric("PE", fmt_num(info.get("pe")))
            v3.metric("Forward PE", fmt_num(info.get("forward_pe")))
            v4, v5, v6 = st.columns(3)
            v4.metric("PB", fmt_num(info.get("pb")))
            v5.metric("殖利率", fmt_pct(info.get("dividend_yield")))
            v6.metric("營收成長", fmt_pct(info.get("revenue_growth")))
        with tab3:
            section("黑天鵝分析")
            st.metric("黑天鵝分數", swan_score)
            for r in swan_reasons:
                st.write(f"- {r}")
            st.info("若未來接上 Telegram，只有劇烈異動才推播。推播時會提醒：請回頭檢查法說、財報、重大公告與新聞。")
        with tab4:
            section("思維模型反問")
            for model, q in thinking_questions():
                with st.expander(model):
                    st.write(q)
                    st.text_area(f"{model}：你的回答", key=f"{ticker}_{model}")
        with tab5:
            section("Investment Thesis")
            current_thesis = thesis_df[thesis_df["ticker"] == ticker]
            if not current_thesis.empty:
                st.dataframe(current_thesis, use_container_width=True, hide_index=True)
            with st.form(f"thesis_form_{ticker}"):
                thesis_text = st.text_area("投資假設")
                risk_text = st.text_area("主要風險")
                check_item = st.text_area("需要驗證的事項")
                if st.form_submit_button("儲存 Thesis"):
                    new = pd.DataFrame([{"ticker": ticker, "thesis": thesis_text, "risk": risk_text, "check_item": check_item, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                    thesis_df = pd.concat([thesis_df, new], ignore_index=True)
                    save_thesis(thesis_df)
                    st.success("已儲存 Thesis")
                    st.rerun()
            st.divider()
            section("我的筆記")
            current_notes = notes[notes["ticker"] == ticker]
            if not current_notes.empty:
                st.dataframe(current_notes, use_container_width=True, hide_index=True)
            with st.form(f"note_form_{ticker}"):
                note_text = st.text_area("新增筆記")
                if st.form_submit_button("儲存筆記"):
                    new_note = pd.DataFrame([{"ticker": ticker, "note": note_text, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                    notes = pd.concat([notes, new_note], ignore_index=True)
                    save_notes(notes)
                    st.success("已儲存筆記")
                    st.rerun()
        with tab6:
            section("Decision Log")
            current_decisions = decision_df[decision_df["ticker"] == ticker]
            if not current_decisions.empty:
                st.dataframe(current_decisions, use_container_width=True, hide_index=True)
            with st.form(f"decision_form_{ticker}"):
                action = st.selectbox("動作", ["研究", "觀察", "買進", "加碼", "減碼", "賣出", "放棄"])
                reason = st.text_area("原因")
                risk = st.text_area("主要風險")
                d_thesis = st.text_area("當時投資假設")
                if st.form_submit_button("儲存 Decision"):
                    new_d = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "ticker": ticker, "action": action, "reason": reason, "risk": risk, "thesis": d_thesis}])
                    decision_df = pd.concat([decision_df, new_d], ignore_index=True)
                    save_decisions(decision_df)
                    st.success("已儲存 Decision")
                    st.rerun()

    st.divider()
    section("新增 / 更新公司")
    with st.form("add_company"):
        ticker = st.text_input("股票代號", placeholder="例如：6969.TW / NVDA / 7203.T")
        name = st.text_input("公司名稱")
        market = st.selectbox("市場", ["台股", "美股", "日股"])
        industry = st.text_input("產業")
        sub_industry = st.text_input("次產業")
        theme = st.text_input("題材")
        main_products = st.text_area("主要產品 / 公司方向")
        business_model = st.text_area("商業模式")
        customers = st.text_area("主要客戶")
        competitors = st.text_area("競爭對手")
        key_questions = st.text_area("關鍵問題")
        status = st.selectbox("狀態", ["持續追蹤", "觀察", "暫停追蹤"])
        if st.form_submit_button("新增 / 更新"):
            if not ticker or not name:
                st.error("股票代號與公司名稱必填。")
            else:
                new_row = pd.DataFrame([{"ticker": ticker.strip(), "name": name.strip(), "market": market, "industry": industry.strip(), "sub_industry": sub_industry.strip(), "theme": theme.strip(), "main_products": main_products.strip(), "business_model": business_model.strip(), "customers": customers.strip(), "competitors": competitors.strip(), "key_questions": key_questions.strip(), "status": status}])
                watchlist = pd.concat([watchlist, new_row], ignore_index=True)
                watchlist = watchlist.drop_duplicates(subset=["ticker"], keep="last")
                save_watchlist(watchlist)
                st.success(f"已新增 / 更新：{ticker} {name}")
                st.rerun()
    section("刪除公司")
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
    section("Black Swan Center", "劇烈波動提醒中心")
    rows = []
    for _, row in watchlist.iterrows():
        p = get_price_data(row["ticker"])
        score, reasons = black_swan_score(p)
        rows.append({"ticker": row["ticker"], "name": row["name"], "market": row["market"], "score": score, "reason": "；".join(reasons)})
    swan_df = pd.DataFrame(rows).sort_values("score", ascending=False)
    st.dataframe(swan_df, use_container_width=True, hide_index=True)

elif page == "Thinking Models":
    section("Thinking Models", "用來反問自己的投資思考工具")
    st.dataframe(pd.DataFrame(thinking_questions(), columns=["model", "question"]), use_container_width=True, hide_index=True)

elif page == "Decision Log":
    section("Decision Log", "先記錄，再檢討")
    st.dataframe(load_decisions(), use_container_width=True, hide_index=True)

elif page == "Settings":
    section("Settings")
    st.markdown("""
    目前版本：**PIOS v1.0 Company Center**

    已完成：
    - 公司中心
    - 股票清單
    - 新增 / 刪除公司
    - yfinance 行情與估值
    - 黑天鵝基本分數
    - 思維模型反問
    - Thesis / 筆記 / Decision Log 雛形

    下一版：
    - Telegram 推播
    - 新聞熱度
    - 法說與財報欄位
    - 永久資料庫
    """)
