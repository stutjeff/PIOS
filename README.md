# PIOS 4.0 Enterprise v0.5

PIOS 4.0 是個人投資作業系統的正式產品化骨架。

## v0.5 重點

- 新增正式市場壓力雷達 `real_market_pressure`
- 新增台股核心追蹤雷達 `taiwan_core_watch`
- PIOS 總分改為加權決策引擎
- mock_market 降為低權重測試資料，不再主導決策
- 首頁正式資料與 mock 測試資料分離顯示
- Yahoo Finance 加入 QQQ、VIX、TLT、00662、00670L、00865B、2002、6969 追蹤

## 操作

```bash
pip install -r requirements.txt
python scripts/run_once.py
streamlit run app.py
```

## 注意

`6969.TWO` 在 Yahoo 可能查無資料，這會顯示為 partial/fail，但不會讓系統掛掉。
這是預期行為。
