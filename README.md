# PIOS 4.0 Enterprise

PIOS 4.0 是個人投資作業系統的正式產品化骨架。

## 目標

- 資料源可替換：官方資料、券商 API、公開資訊觀測站、交易所、手動輸入都能接上。
- 雷達規則獨立：市場壓力、融資槓桿、信用利差、個股事件、估值系統互不綁死。
- 資料庫先行：所有訊號留下歷史紀錄，未來才能回測與改善。
- UI 只是入口：Streamlit 負責看結果，不把核心邏輯寫死在頁面。

## 安裝

```bash
pip install -r requirements.txt
cp .env.example .env
```

## 執行一次資料與雷達流程

```bash
python scripts/run_once.py
```

## 啟動 Streamlit

```bash
streamlit run app.py
```

## 啟動排程

```bash
python scheduler/jobs.py
```

## v0.2 升級重點

- 不清空原 GitHub Repo，直接覆蓋升級。
- 新增 root app.py，Streamlit Cloud 建議指向 app.py。
- 建立 modules/ 長期模組區。
- 預留 TWSE、MOPS、成信追蹤雷達接口。
- scripts/run_once.py 加入 import path 保護。

## 目前版本內容

- SQLite 資料庫
- MarketSnapshot 資料表
- RadarSignal 資料表
- MockMarketSource 示範資料源
- MarketPressureRadar 示範雷達
- Streamlit 主控台
- 08:00 / 22:00 排程骨架

## 下一步

1. 接入台股官方資料源。
2. 接入公開資訊觀測站重大公告。
3. 接入法人買賣與融資融券資料。
4. 建立成信 6969 事件雷達。
5. 加入 Telegram 推播。
6. 加入回測與訊號品質檢查。
