# PIOS 4.0 Enterprise v0.7

個人投資作業系統 Enterprise 架構。

## v0.7 新增

- 新聞智慧化 News Intelligence
- 新聞自動分類：AI資料中心/電力、美債/利率、台股ETF、成信6969、半導體、能源、美股科技
- 新聞影響分數 impact_score
- 新聞風險分數 risk_score
- 關聯標的判讀：6969、00662、00670L、00865B/TLT、QQQ、電網、AI散熱
- 個人專屬新聞流：依影響分數排序，不再只列 RSS
- 新聞摘要欄位：每則新聞自動產生一行判讀
- SQLite 輕量 migration：既有 `news_items` 會自動補欄位
- News Radar 納入新聞分類與平均影響力

## v0.6 保留

- Google News RSS 資料源，不需要 API key
- Finnhub News 支援 API key：`FINNHUB_API_KEY`
- Marketaux News 支援 API key：`MARKETAUX_API_KEY`
- 新聞資料表 `news_items`
- 首頁「抓取新聞」與新聞雷達區塊
- PIOS Score 納入新聞雷達權重

## Streamlit Secrets 可選

```toml
FINNHUB_API_KEY="你的 key"
MARKETAUX_API_KEY="你的 key"
```

沒有 API key 也可以先跑 Google News RSS。

## 執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 排程

```bash
python scripts/run_once.py
```
