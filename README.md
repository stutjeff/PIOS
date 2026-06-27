# PIOS 4.0 Enterprise

PIOS 4.0 是個人投資作業系統的正式產品化骨架。

## v0.4 重點

- Yahoo Finance 改為「單一 symbol 失敗不拖垮整個資料源」
- Yahoo 404/缺資料會寫入 `source_symbol_error`，方便 UI 追蹤
- DataSourceManager 支援 partial success
- 新增 PIOS 總分與 514 / 433 建議模式
- 首頁升級成作戰總覽：總分、模式、資料源健康、快照、雷達訊號

## 本地執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 單次批次執行

```bash
python scripts/run_once.py
```
