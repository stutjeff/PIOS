from __future__ import annotations

import streamlit as st
from sqlalchemy import select

from core.settings import load_settings
from storage.db import init_db, db_session
from storage.models import RadarSignal, MarketSnapshot
from data_sources.mock_source import MockMarketSource
from services.ingestion import save_datapoints
from services.radar_runner import run_all_radars


def main() -> None:
    settings = load_settings()
    st.set_page_config(page_title=settings.app.name, layout="wide")
    init_db()

    st.title("PIOS 4.0 Enterprise")
    st.caption("個人投資作業系統：資料、雷達、規則、紀律。UI 只是駕駛艙，不是把引擎綁死在方向盤上。")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("抓取示範資料"):
            count = save_datapoints(MockMarketSource().fetch())
            st.success(f"已寫入 {count} 筆資料")

    with col2:
        if st.button("執行雷達"):
            signals = run_all_radars()
            st.success(f"已產生 {len(signals)} 筆雷達訊號")

    with col3:
        st.metric("目前模式", settings.portfolio.get("modes", {}).get("normal", "514"))

    st.divider()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("最新雷達訊號")
        with db_session() as session:
            rows = session.execute(
                select(RadarSignal).order_by(RadarSignal.created_at.desc()).limit(10)
            ).scalars().all()
        if rows:
            for r in rows:
                st.write(f"**{r.radar_name}**｜{r.level}｜{r.score}")
                st.caption(r.summary)
        else:
            st.info("尚無雷達訊號。先抓資料，再執行雷達。")

    with right:
        st.subheader("最新資料快照")
        with db_session() as session:
            snapshots = session.execute(
                select(MarketSnapshot).order_by(MarketSnapshot.captured_at.desc()).limit(20)
            ).scalars().all()
        if snapshots:
            st.dataframe([
                {
                    "source": s.source,
                    "symbol": s.symbol,
                    "metric": s.metric,
                    "value": s.value,
                    "captured_at": s.captured_at,
                }
                for s in snapshots
            ], use_container_width=True)
        else:
            st.info("尚無資料。")


if __name__ == "__main__":
    main()
