# PIOS 4.0 Enterprise v0.2 升級方式

## 建議方式

不要清空 GitHub Repository。

直接把這包 zip 解壓縮後，全部檔案上傳到原本的 `PIOS` Repository，遇到同名檔案選擇覆蓋。

## Streamlit 啟動檔

建議使用：

```bash
streamlit run app.py
```

`app.py` 會轉接到 `app/main.py`，未來 Streamlit Cloud 比較不容易迷路。

## 本機測試

```bash
pip install -r requirements.txt
python scripts/run_once.py
streamlit run app.py
```

## v0.2 重點

- 保留原 Repo，不重開、不清空。
- 新增 root `app.py`，降低 Streamlit 部署錯誤率。
- `scripts/run_once.py` 自動修正 import path。
- 建立 `modules/` 長期擴充區。
- 預留 TWSE、MOPS、成信追蹤雷達接口。
