# PIOS 4.0 Enterprise

PIOS 4.0 是個人投資作業系統的正式產品化骨架。

## v0.3 重點

- 新增 DataSourceManager：所有資料源統一入口
- 新增 SourceRun：追蹤每次資料源執行成功/失敗
- 新增 YahooFinanceSource：核心 ETF / 個股價格來源
- 新增 TWSESource：證交所官方 open-data 健康檢查接口
- Streamlit 首頁新增資料源健康狀態
- `scripts/run_once.py` 可給 GitHub Actions 排程使用

## 本地執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 單次批次執行

```bash
python scripts/run_once.py
```
