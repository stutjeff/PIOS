# PIOS 4.0 Enterprise v1.0 Alpha

PIOS 是個人投資作業系統。v1.0 Alpha 的目標不是再加幾個按鈕，而是把資料源、新聞、雷達、總分、警報、匯出與排程整理成可持續擴充的產品骨架。

## 本版新增

- 全系統更新：市場資料、新聞、智慧標籤、雷達、警報一次執行
- PIOS 壓力分正式化：多雷達加權，支援分數歷史
- 雷達分數拆解：看得出總分怎麼來
- 警報中心：雷達與高影響新聞自動產生 alert
- 新聞中心：分類、影響分數、風險分數、關聯標的、摘要
- 個人專屬新聞流：按 impact_score 排序
- 全球資料擴充：QQQ、SPY、IWM、SOXX、VIX、TLT、UUP、GLD、USO、CPER、BTC-USD
- 台股核心資料：00662、00670L、00865B、2002；6969 允許 Yahoo partial fail
- CSV 匯出：market_snapshots、news_items、radar_signals、source_runs、pios_score_history、alert_events
- SQLite 自動 migration：舊資料庫可直接升級

## Streamlit 主程式

```txt
app.py
```

## 必要套件

```txt
streamlit>=1.36.0
SQLAlchemy>=2.0.0
PyYAML>=6.0.0
pandas>=2.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

## 可選 API Key

`.env` 或 Streamlit Secrets：

```txt
FINNHUB_API_KEY=
MARKETAUX_API_KEY=
```

沒有 API key 也能使用 Google News RSS。

## 建議使用流程

1. 按「全系統更新」
2. 看 PIOS 壓力分與建議模式
3. 看警報中心
4. 看個人專屬新聞流
5. 有異常再進資料健康與匯出頁面

## 注意

PIOS 是決策輔助系統，不是自動下單系統。分數是壓力分，越高代表越需要保守，不代表越值得買。
