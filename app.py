import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="PIOS",
    page_icon="📈",
    layout="wide"
)

WATCHLIST_FILE = Path("watchlist.csv")
NOTES_FILE = Path("company_notes.csv")
THESIS_FILE = Path("investment_thesis.csv")
DECISION_FILE = Path("decision_log.csv")
EARNINGS_FILE = Path("earnings_notes.csv")
REPORT_FILE = Path("financial_notes.csv")
NEWS_FILE = Path("news_notes.csv")

REQUIRED_COLUMNS = [
    "ticker", "name", "market", "industry", "sub_industry", "theme",
    "main_products", "business_model", "customers", "suppliers",
    "competitors", "moat", "management", "key_questions", "status"
]

MARKET_ORDER = {"台股": 1, "美股": 2, "日股": 3}


DEFAULT_DATA = [
    {
        "ticker": "6969.TW",
        "name": "成信",
        "market": "台股",
        "industry": "環保回收",
        "sub_industry": "半導體循環經濟",
        "theme": "半導體、循環經濟、零廢製造",
        "main_products": "CMP研磨材料回收、功能性陶瓷粉體、電子級二氧化矽",
        "business_model": "承接半導體相關廢棄物與副產物，透過回收、純化與再利用技術轉為可銷售材料。",
        "customers": "台積電供應鏈、日月光供應鏈、半導體與電子材料客戶",
        "suppliers": "半導體廢棄物來源、回收處理設備與材料供應商",
        "competitors": "其他環保處理商、半導體廢棄物回收商、材料再生業者",
        "moat": "驗證門檻、法規門檻、客戶導入時間、回收純化技術。",
        "management": "待補充",
        "key_questions": "中科處理額度是否放寬？球形二氧化矽驗證是否完成？南科零廢中心是否落地？",
        "status": "核心觀察",
    },
    {
        "ticker": "1513.TW",
        "name": "中興電",
        "market": "台股",
        "industry": "電機設備",
        "sub_industry": "重電 / 電網",
        "theme": "電網升級、AI電力、能源轉型",
        "main_products": "重電設備、變電設備、電力工程、智慧電網相關設備",
        "business_model": "提供電力基礎建設設備與工程服務，受惠電網升級與用電需求增加。",
        "customers": "台電、公共工程、民間電力建設客戶",
        "suppliers": "鋼材、銅材、電力設備零組件供應商",
        "competitors": "華城、士電、國際重電設備商",
        "moat": "本土電網標案經驗、設備認證、市占與工程履歷。",
        "management": "待補充",
        "key_questions": "訂單能見度是否延續？毛利率是否維持？AI電力需求是否實際反映？",
        "status": "持續追蹤",
    },
    {
        "ticker": "8936.TW",
        "name": "國統",
        "market": "台股",
        "industry": "水資源",
        "sub_industry": "管線 / 海淡 / 再生水",
        "theme": "水資源、海淡、極端氣候",
        "main_products": "管線工程、水資源工程、海淡與再生水相關工程",
        "business_model": "承接大型管線、水資源與海淡再生水工程，受惠水資源基礎建設。",
        "customers": "政府標案、公用事業、工業用水需求者",
        "suppliers": "管材、工程設備、施工承包商",
        "competitors": "水資源工程承包商、管線工程公司",
        "moat": "大型管線工程經驗、工程履歷、標案資格。",
        "management": "待補充",
        "key_questions": "海淡與再生水標案是否增加？工程毛利率是否改善？營運權是否擴大？",
        "status": "持續追蹤",
    },
    {
        "ticker": "2308.TW",
        "name": "台達電",
        "market": "台股",
        "industry": "電源 / 散熱",
        "sub_industry": "AI資料中心 / 能源管理",
        "theme": "AI資料中心、電源、液冷、能源管理",
        "main_products": "電源供應器、散熱、工業自動化、能源管理、資料中心解決方案",
        "business_model": "提供高效率電源、散熱與能源管理方案，受惠AI資料中心與電氣化趨勢。",
        "customers": "資料中心、伺服器、工業自動化、電動車與能源客戶",
        "suppliers": "功率半導體、磁性元件、機構件、電子零組件供應商",
        "competitors": "Vertiv、Schneider Electric、其他電源與散熱供應商",
        "moat": "規模、客戶黏著度、能源效率技術、完整產品線。",
        "management": "待補充",
        "key_questions": "AI資料中心需求是否持續？液冷與電源產品毛利率如何？估值是否過熱？",
        "status": "持續追蹤",
    },
    {
        "ticker": "NVDA",
        "name": "NVIDIA",
        "market": "美股",
        "industry": "半導體",
        "sub_industry": "AI晶片",
        "theme": "AI、GPU、資料中心",
        "main_products": "GPU、AI加速器、資料中心平台、CUDA生態系",
        "business_model": "銷售AI晶片、資料中心平台與軟硬整合解決方案。",
        "customers": "雲端服務商、AI模型公司、企業資料中心",
        "suppliers": "台積電、封裝、記憶體、伺服器供應鏈",
        "competitors": "AMD、Broadcom、ASIC供應商、雲端自研晶片",
        "moat": "CUDA生態系、軟硬整合、規模、開發者黏著度。",
        "management": "待補充",
        "key_questions": "AI資本支出是否維持？毛利率是否下滑？競爭者ASIC是否侵蝕需求？",
        "status": "持續追蹤",
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft",
        "market": "美股",
        "industry": "軟體 / 雲端",
        "sub_industry": "AI雲端",
        "theme": "AI、雲端、企業軟體",
        "main_products": "Azure、Office、Windows、Copilot、企業雲端服務",
        "business_model": "以雲端、訂閱制軟體與企業服務創造穩定現金流。",
        "customers": "企業、政府、個人用戶、開發者",
        "suppliers": "資料中心、晶片、軟體生態系供應商",
        "competitors": "Google、Amazon、Oracle、Salesforce",
        "moat": "企業客戶黏著度、雲端平台、軟體生態系。",
        "management": "待補充",
        "key_questions": "AI投入是否轉化為收入？Azure成長是否延續？資本支出壓力是否上升？",
        "status": "持續追蹤",
    },
    {
        "ticker": "CEG",
        "name": "Constellation Energy",
        "market": "美股",
        "industry": "電力",
        "sub_industry": "核電 / 資料中心電力",
        "theme": "核電、AI資料中心電力、長約供電",
        "main_products": "核電、電力供應、能源合約",
        "business_model": "提供穩定低碳電力，受惠資料中心長期用電需求。",
        "customers": "公用事業、企業客戶、資料中心",
        "suppliers": "核燃料、電網與能源設備供應商",
        "competitors": "其他電力公司、再生能源供應商、天然氣發電商",
        "moat": "既有核電資產、長期供電合約、穩定基載電力。",
        "management": "待補充",
        "key_questions": "AI資料中心長約是否增加？核電政策是否支持？電價與資本支出如何變化？",
        "status": "持續追蹤",
    },
    {
        "ticker": "7203.T",
        "name": "Toyota",
        "market": "日股",
        "industry": "汽車",
        "sub_industry": "混合動力 / 自動化",
        "theme": "混合動力、全球汽車、自動化",
        "main_products": "汽車、混合動力車、商用車",
        "business_model": "全球汽車製造與銷售，混合動力與供應鏈管理為重要優勢。",
        "customers": "全球汽車消費者、商用車客戶",
        "suppliers": "汽車零組件、電池、半導體與材料供應商",
        "competitors": "Volkswagen、Hyundai、Tesla、中國車企",
        "moat": "製造能力、品牌、供應鏈管理、混合動力技術。",
        "management": "待補充",
        "key_questions": "混合動力優勢是否延續？電動車轉型是否落後？匯率是否影響獲利？",
        "status": "觀察",
    },
]


def normalize_ticker(ticker, market=None):
    raw = str(ticker).strip()
    if not raw:
        return ""

    t = raw.upper().replace(" ", "")

    # Normalize common Taiwan / Japan suffixes
    t = t.replace(".TW", ".TW").replace(".TWO", ".TWO").replace(".T", ".T")

    if market == "台股":
        if re.fullmatch(r"\d{4}", t):
            return f"{t}.TW"
        if t.endswith(".TW") or t.endswith(".TWO"):
            return t
        return t

    if market == "日股":
        if re.fullmatch(r"\d{4}", t):
            return f"{t}.T"
        if t.endswith(".T"):
            return t
        return t

    if market == "美股":
        return t.replace(".US", "")

    return t


def ticker_sort_key(ticker):
    t = str(ticker).upper()
    m = re.search(r"\d+", t)
    if m:
        return (0, int(m.group()), t)
    return (1, 999999, t)


def sort_watchlist(df):
    df = df.copy()
    df["ticker"] = df.apply(lambda r: normalize_ticker(r["ticker"], r["market"]), axis=1)
    df["_market_order"] = df["market"].map(MARKET_ORDER).fillna(99)
    df["_ticker_num"] = df["ticker"].apply(lambda x: ticker_sort_key(x)[1])
    df["_ticker_alpha"] = df["ticker"].astype(str).str.upper()
    df = df.sort_values(["_market_order", "_ticker_num", "_ticker_alpha", "name"])
    return df.drop(columns=["_market_order", "_ticker_num", "_ticker_alpha"])


def init_csv(path, columns):
    if not path.exists():
        pd.DataFrame(columns=columns).to_csv(path, index=False)


def init_watchlist():
    if not WATCHLIST_FILE.exists():
        pd.DataFrame(DEFAULT_DATA).to_csv(WATCHLIST_FILE, index=False)


def load_watchlist():
    init_watchlist()
    df = pd.read_csv(WATCHLIST_FILE)
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[REQUIRED_COLUMNS]
    df = sort_watchlist(df)
    return df


def save_watchlist(df):
    df = sort_watchlist(df)
    df.to_csv(WATCHLIST_FILE, index=False)


def load_table(path, columns):
    init_csv(path, columns)
    return pd.read_csv(path)


def save_table(df, path):
    df.to_csv(path, index=False)


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
        low_52w = float(close.min())
        drop_from_high = (latest_close / high_52w - 1) * 100
        avg_volume_20 = float(volume.tail(20).mean())
        latest_volume = float(volume.iloc[-1])
        volume_ratio = latest_volume / avg_volume_20 if avg_volume_20 > 0 else 0
        return {
            "price": latest_close,
            "daily_change": daily_change,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "drop_from_high": drop_from_high,
            "volume_ratio": volume_ratio,
        }
    except Exception:
        return None


@st.cache_data(ttl=3600)
def get_info(ticker):
    try:
        info = yf.Ticker(ticker).info or {}
        return {
            "market_cap": info.get("marketCap"),
            "pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "roe": info.get("returnOnEquity"),
            "profit_margin": info.get("profitMargins"),
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


def fmt_pct(value, already_pct=False):
    if value is None or pd.isna(value):
        return "—"
    try:
        v = float(value)
        if not already_pct:
            v *= 100
        return f"{v:.2f}%"
    except Exception:
        return "—"


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


def status_badge(status):
    mapping = {
        "核心觀察": "🔵 核心觀察",
        "持續追蹤": "🟢 持續追蹤",
        "觀察": "🟡 觀察",
        "暫停追蹤": "⚪ 暫停追蹤",
    }
    return mapping.get(str(status), str(status))


def score_badge(score):
    if score >= 85:
        return "S"
    if score >= 75:
        return "A"
    if score >= 60:
        return "B"
    if score >= 45:
        return "C"
    return "D"


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


def score_slider(label, default=70, key=None):
    value = st.slider(label, 0, 100, default, key=key)
    st.progress(value / 100)
    return value


def market_group_label(market, count):
    icon = {"台股": "🇹🇼", "美股": "🇺🇸", "日股": "🇯🇵"}.get(market, "🌐")
    return f"{icon} {market}（{count}）"


def render_company_picker(df):
    selected_ticker = None
    for market in ["台股", "美股", "日股"]:
        group = df[df["market"] == market]
        if group.empty:
            continue
        with st.sidebar.expander(market_group_label(market, len(group)), expanded=True):
            labels = (group["ticker"] + "｜" + group["name"]).tolist()
            key = f"company_radio_{market}"
            chosen = st.radio("公司", labels, key=key, label_visibility="collapsed")
            if chosen and selected_ticker is None:
                selected_ticker = chosen.split("｜")[0]
    return selected_ticker


st.title("📈 PIOS")
st.caption("Personal Investment Operating System｜v1.2 Watchlist Sorting")

watchlist = load_watchlist()
notes_df = load_table(NOTES_FILE, ["ticker", "note", "updated_at"])
thesis_df = load_table(THESIS_FILE, ["ticker", "thesis", "risk", "sell_condition", "confidence", "updated_at"])
decision_df = load_table(DECISION_FILE, ["date", "ticker", "action", "reason", "risk", "thesis"])
earnings_df = load_table(EARNINGS_FILE, ["ticker", "date", "summary", "opportunity", "risk", "updated_at"])
report_df = load_table(REPORT_FILE, ["ticker", "date", "revenue", "eps", "margin", "cashflow", "summary", "updated_at"])
news_df = load_table(NEWS_FILE, ["ticker", "date", "title", "importance", "summary", "updated_at"])

st.sidebar.title("PIOS")
page = st.sidebar.radio(
    "選單",
    ["Dashboard", "Company Center", "Watchlist", "Black Swan", "Thinking Models", "Decision Log", "Settings"],
)

if page == "Dashboard":
    section("Today's Focus", "今天最值得你注意的事情")
    st.info("目前沒有需要立即處理的重要事件。")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("台股", len(watchlist[watchlist["market"] == "台股"]))
    c2.metric("美股", len(watchlist[watchlist["market"] == "美股"]))
    c3.metric("日股", len(watchlist[watchlist["market"] == "日股"]))
    c4.metric("公司總數", len(watchlist))

    st.divider()
    section("Watchlist Overview", "已依台股 → 美股 → 日股，以及代號大小排序")
    show = watchlist[["ticker", "name", "market", "industry", "theme", "status"]].copy()
    show["status"] = show["status"].apply(status_badge)
    st.dataframe(show, use_container_width=True, hide_index=True)

elif page == "Company Center":
    section("Company Center", "公司研究中心")

    market_filter = st.sidebar.selectbox("市場篩選", ["全部", "台股", "美股", "日股"])
    status_filter = st.sidebar.selectbox("狀態篩選", ["全部", "核心觀察", "持續追蹤", "觀察", "暫停追蹤"])

    filtered = watchlist.copy()
    if market_filter != "全部":
        filtered = filtered[filtered["market"] == market_filter]
    if status_filter != "全部":
        filtered = filtered[filtered["status"] == status_filter]

    if filtered.empty:
        st.warning("目前沒有符合條件的公司。")
    else:
        ticker = render_company_picker(filtered)
        if ticker is None:
            st.stop()

        company = watchlist[watchlist["ticker"] == ticker].iloc[0]

        price = get_price_data(ticker)
        info = get_info(ticker)
        swan, swan_reasons = black_swan_score(price)

        st.markdown(f"# {company['name']} ({company['ticker']})")
        st.caption(f"{status_badge(company['status'])}｜{company['market']}｜{company['industry']}｜{company['sub_industry']}")

        k1, k2, k3, k4 = st.columns(4)
        if price:
            k1.metric("收盤價", f"{price['price']:.2f}", f"{price['daily_change']:+.2f}%")
            k2.metric("52週高點回落", fmt_pct(price["drop_from_high"], already_pct=True))
            k3.metric("量能倍率", f"{price['volume_ratio']:.2f}x")
        else:
            k1.metric("收盤價", "—")
            k2.metric("52週高點回落", "—")
            k3.metric("量能倍率", "—")
        k4.metric("黑天鵝分數", swan, score_badge(swan))

        tab_company, tab_value, tab_report, tab_call, tab_news, tab_think, tab_thesis, tab_log = st.tabs(
            ["公司", "估值", "財報", "法說", "新聞", "思維模型", "Thesis / 筆記", "Decision Log"]
        )

        with tab_company:
            section("公司概況")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**主要題材：** {company['theme']}")
                st.write(f"**主要產品：** {company['main_products']}")
                st.write(f"**商業模式：** {company['business_model']}")
                st.write(f"**護城河：** {company['moat']}")
            with col_b:
                st.write(f"**主要客戶：** {company['customers']}")
                st.write(f"**主要供應商：** {company['suppliers']}")
                st.write(f"**競爭對手：** {company['competitors']}")
                st.write(f"**管理層：** {company['management']}")
            st.info(f"關鍵問題：{company['key_questions']}")

        with tab_value:
            section("估值 / 基本面", "資料來源：yfinance，台股資料可能不完整")
            v1, v2, v3 = st.columns(3)
            v1.metric("市值", fmt_num(info.get("market_cap")))
            v2.metric("PE", fmt_num(info.get("pe")))
            v3.metric("Forward PE", fmt_num(info.get("forward_pe")))
            v4, v5, v6 = st.columns(3)
            v4.metric("PB", fmt_num(info.get("pb")))
            v5.metric("殖利率", fmt_pct(info.get("dividend_yield")))
            v6.metric("ROE", fmt_pct(info.get("roe")))

        with tab_report:
            section("財報中心")
            current = report_df[report_df["ticker"] == ticker]
            if not current.empty:
                st.dataframe(current, use_container_width=True, hide_index=True)

            with st.form(f"report_{ticker}"):
                date = st.text_input("財報日期", placeholder="2026-Q1 / 2026-06-30")
                revenue = st.text_input("營收")
                eps = st.text_input("EPS")
                margin = st.text_input("毛利率 / 營益率")
                cashflow = st.text_input("自由現金流 / 現金流")
                summary = st.text_area("財報重點")
                ok = st.form_submit_button("儲存財報紀錄")
                if ok:
                    new = pd.DataFrame([{
                        "ticker": ticker,
                        "date": date,
                        "revenue": revenue,
                        "eps": eps,
                        "margin": margin,
                        "cashflow": cashflow,
                        "summary": summary,
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }])
                    report_df = pd.concat([report_df, new], ignore_index=True)
                    save_table(report_df, REPORT_FILE)
                    st.success("已儲存財報紀錄")
                    st.rerun()

        with tab_call:
            section("法說中心")
            current = earnings_df[earnings_df["ticker"] == ticker]
            if not current.empty:
                st.dataframe(current, use_container_width=True, hide_index=True)

            with st.form(f"call_{ticker}"):
                date = st.text_input("法說日期", placeholder="2026-06-27")
                summary = st.text_area("管理層重點")
                opportunity = st.text_area("機會")
                risk = st.text_area("風險")
                ok = st.form_submit_button("儲存法說紀錄")
                if ok:
                    new = pd.DataFrame([{
                        "ticker": ticker,
                        "date": date,
                        "summary": summary,
                        "opportunity": opportunity,
                        "risk": risk,
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }])
                    earnings_df = pd.concat([earnings_df, new], ignore_index=True)
                    save_table(earnings_df, EARNINGS_FILE)
                    st.success("已儲存法說紀錄")
                    st.rerun()

        with tab_news:
            section("新聞中心")
            current = news_df[news_df["ticker"] == ticker]
            if not current.empty:
                st.dataframe(current, use_container_width=True, hide_index=True)

            with st.form(f"news_{ticker}"):
                date = st.text_input("新聞日期", placeholder="2026-06-27")
                title = st.text_input("新聞標題")
                importance = st.selectbox("重要性", ["低", "中", "高", "重大"])
                summary = st.text_area("摘要 / 對投資假設的影響")
                ok = st.form_submit_button("儲存新聞")
                if ok:
                    new = pd.DataFrame([{
                        "ticker": ticker,
                        "date": date,
                        "title": title,
                        "importance": importance,
                        "summary": summary,
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }])
                    news_df = pd.concat([news_df, new], ignore_index=True)
                    save_table(news_df, NEWS_FILE)
                    st.success("已儲存新聞")
                    st.rerun()

        with tab_think:
            section("思維模型評分")
            c1, c2 = st.columns(2)
            with c1:
                trend = score_slider("長期趨勢", 80, f"{ticker}_trend")
                moat = score_slider("護城河", 70, f"{ticker}_moat")
                finance = score_slider("財務品質", 60, f"{ticker}_finance")
            with c2:
                valuation = score_slider("估值合理性", 60, f"{ticker}_valuation")
                risk = score_slider("風險可控性", 60, f"{ticker}_risk")
                understanding = score_slider("我的理解程度", 70, f"{ticker}_understanding")
            total = round((trend + moat + finance + valuation + risk + understanding) / 6)
            st.metric("思維模型總分", total, score_badge(total))

            st.divider()
            section("蘇格拉底式反問")
            for model, question in thinking_questions():
                with st.expander(model):
                    st.write(question)
                    st.text_area("你的回答", key=f"{ticker}_{model}")

        with tab_thesis:
            section("Investment Thesis")
            current = thesis_df[thesis_df["ticker"] == ticker]
            if not current.empty:
                st.dataframe(current, use_container_width=True, hide_index=True)

            with st.form(f"thesis_{ticker}"):
                thesis_text = st.text_area("我為什麼看好 / 追蹤？")
                risk_text = st.text_area("最大的風險")
                sell_condition = st.text_area("什麼情況會賣出 / 放棄？")
                confidence = st.slider("目前信心", 0, 100, 70)
                ok = st.form_submit_button("儲存 Thesis")
                if ok:
                    new = pd.DataFrame([{
                        "ticker": ticker,
                        "thesis": thesis_text,
                        "risk": risk_text,
                        "sell_condition": sell_condition,
                        "confidence": confidence,
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }])
                    thesis_df = pd.concat([thesis_df, new], ignore_index=True)
                    save_table(thesis_df, THESIS_FILE)
                    st.success("已儲存 Thesis")
                    st.rerun()

            st.divider()
            section("我的筆記")
            current_notes = notes_df[notes_df["ticker"] == ticker]
            if not current_notes.empty:
                st.dataframe(current_notes, use_container_width=True, hide_index=True)

            with st.form(f"note_{ticker}"):
                note = st.text_area("新增筆記")
                ok = st.form_submit_button("儲存筆記")
                if ok:
                    new = pd.DataFrame([{
                        "ticker": ticker,
                        "note": note,
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }])
                    notes_df = pd.concat([notes_df, new], ignore_index=True)
                    save_table(notes_df, NOTES_FILE)
                    st.success("已儲存筆記")
                    st.rerun()

        with tab_log:
            section("Decision Log")
            current = decision_df[decision_df["ticker"] == ticker]
            if not current.empty:
                st.dataframe(current, use_container_width=True, hide_index=True)

            with st.form(f"decision_{ticker}"):
                action = st.selectbox("動作", ["研究", "觀察", "買進", "加碼", "減碼", "賣出", "放棄"])
                reason = st.text_area("原因")
                risk = st.text_area("主要風險")
                d_thesis = st.text_area("當時投資假設")
                ok = st.form_submit_button("儲存 Decision")
                if ok:
                    new = pd.DataFrame([{
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "ticker": ticker,
                        "action": action,
                        "reason": reason,
                        "risk": risk,
                        "thesis": d_thesis,
                    }])
                    decision_df = pd.concat([decision_df, new], ignore_index=True)
                    save_table(decision_df, DECISION_FILE)
                    st.success("已儲存 Decision")
                    st.rerun()

elif page == "Watchlist":
    section("Watchlist 管理", "新增、刪除與排序股票")

    st.info("排序規則：台股 → 美股 → 日股；同市場內依股票代碼由小到大排列。")

    show = watchlist[["ticker", "name", "market", "industry", "theme", "status"]].copy()
    show["status"] = show["status"].apply(status_badge)
    st.dataframe(show, use_container_width=True, hide_index=True)

    st.divider()
    section("新增 / 更新公司")
    with st.form("add_company"):
        cols = st.columns(2)
        with cols[0]:
            ticker_raw = st.text_input("股票代號", placeholder="例如：6641.tw / NVDA / 7203.t")
            name = st.text_input("公司名稱")
            market = st.selectbox("市場", ["台股", "美股", "日股"])
            status = st.selectbox("狀態", ["核心觀察", "持續追蹤", "觀察", "暫停追蹤"])
        with cols[1]:
            industry = st.text_input("產業")
            sub_industry = st.text_input("次產業")
            theme = st.text_input("題材")
        main_products = st.text_area("主要產品")
        business_model = st.text_area("商業模式")
        customers = st.text_area("主要客戶")
        suppliers = st.text_area("主要供應商")
        competitors = st.text_area("競爭對手")
        moat = st.text_area("護城河摘要")
        management = st.text_area("管理層")
        key_questions = st.text_area("關鍵問題")
        ok = st.form_submit_button("新增 / 更新公司")
        if ok:
            ticker = normalize_ticker(ticker_raw, market)
            if not ticker or not name:
                st.error("股票代號與公司名稱必填。")
            else:
                new = pd.DataFrame([{
                    "ticker": ticker,
                    "name": name.strip(),
                    "market": market,
                    "industry": industry.strip(),
                    "sub_industry": sub_industry.strip(),
                    "theme": theme.strip(),
                    "main_products": main_products.strip(),
                    "business_model": business_model.strip(),
                    "customers": customers.strip(),
                    "suppliers": suppliers.strip(),
                    "competitors": competitors.strip(),
                    "moat": moat.strip(),
                    "management": management.strip(),
                    "key_questions": key_questions.strip(),
                    "status": status,
                }])
                watchlist = pd.concat([watchlist, new], ignore_index=True)
                watchlist = watchlist.drop_duplicates(subset=["ticker"], keep="last")
                save_watchlist(watchlist)
                st.success(f"已新增 / 更新並排序：{ticker} {name}")
                st.rerun()

    st.divider()
    section("刪除公司")
    delete_ticker = st.selectbox("選擇要刪除的股票", [""] + watchlist["ticker"].astype(str).tolist())
    if st.button("刪除公司"):
        if delete_ticker:
            watchlist = watchlist[watchlist["ticker"] != delete_ticker]
            save_watchlist(watchlist)
            st.success(f"已刪除：{delete_ticker}")
            st.rerun()

elif page == "Black Swan":
    section("Black Swan Center", "劇烈波動提醒中心")
    rows = []
    for _, row in watchlist.iterrows():
        p = get_price_data(row["ticker"])
        score, reasons = black_swan_score(p)
        rows.append({
            "ticker": row["ticker"],
            "name": row["name"],
            "market": row["market"],
            "score": score,
            "reason": "；".join(reasons),
        })
    df = pd.DataFrame(rows).sort_values(["market", "score"], ascending=[True, False])
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Thinking Models":
    section("Thinking Models", "用來反問自己的投資思考工具")
    st.dataframe(pd.DataFrame(thinking_questions(), columns=["model", "question"]), use_container_width=True, hide_index=True)

elif page == "Decision Log":
    section("Decision Log", "先記錄，再檢討")
    st.dataframe(decision_df, use_container_width=True, hide_index=True)

elif page == "Settings":
    section("Settings")
    st.markdown(
        """
        目前版本：**PIOS v1.2 Watchlist Sorting**

        本版重點：
        - 新增 Watchlist 管理頁
        - 新增 / 刪除公司移出 Company Center
        - 股票自動標準化：6641.tw → 6641.TW，7203.t → 7203.T，nvda → NVDA
        - 依市場分組：台股 → 美股 → 日股
        - 同市場內依代號大小排序
        - 側邊欄公司清單分組顯示
        """
    )
