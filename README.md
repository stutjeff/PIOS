# PIOS 4.0 Enterprise v0.6

個人投資作業系統 Enterprise 架構。

## v0.6 新增

- News Radar 新聞雷達
- Google News RSS 資料源，不需要 API key
- Finnhub News 支援 API key：`FINNHUB_API_KEY`
- Marketaux News 支援 API key：`MARKETAUX_API_KEY`
- 新聞資料表 `news_items`
- 首頁新增「抓取新聞」與新聞雷達區塊
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
