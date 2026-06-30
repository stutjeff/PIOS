from __future__ import annotations

import streamlit as st
from sqlalchemy import select

from core.settings import load_settings
from data_sources.manager import build_default_manager
from radars.decision import latest_pios_decision
from services.news_ingestion import build_default_news_manager
from services.news_intelligence import enrich_recent_news, build_personal_news_digest
from services.radar_runner import run_all_radars
from storage.db import init_db, db_session
from storage.models import MarketSnapshot, NewsItem, RadarSignal, SourceRun


def _level_icon(level: str) -> str:
    return {"green": "🟢", "yellow": "🟡", "red": "🔴", "gray": "⚪"}.get(level, "⚪")


def main() -> None:
    settings = load_settings()
    st.set_page_config(page_title=settings.app.name, layout="wide")
    init_db()

    st.title("PIOS 4.0 Enterprise")
    st.caption("資料源、新聞、雷達、規則、紀律。UI 是駕駛艙，不是把引擎綁死在方向盤上。")

    decision = latest_pios_decision()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("抓取市場資料", type="primary"):
            results = build_default_manager().fetch_all()
            ok = sum(1 for r in results if r.ok)
            fail = len(results) - ok
            st.success(f"市場資料源完成：成功 {ok}，異常 {fail}")
            for r in results:
                icon = "✅" if r.ok else "⚠️"
                st.write(f"{icon} {r.source}: {r.count} 筆" + (f"｜{r.error}" if r.error else ""))

    with col2:
        if st.button("抓取新聞"):
            results = build_default_news_manager().fetch_all()
            ok = sum(1 for r in results if r.ok)
            fail = len(results) - ok
            st.success(f"新聞資料源完成：成功 {ok}，異常 {fail}")
            for r in results:
                icon = "✅" if r.ok else "⚠️"
                st.write(f"{icon} {r.source}: 新增 {r.count} 則" + (f"｜{r.error}" if r.error else ""))
            updated = enrich_recent_news()
            st.caption(f"已完成新聞智慧化：更新 {updated} 則分類/摘要/關聯標的")

    with col3:
        if st.button("執行雷達"):
            updated = enrich_recent_news()
            signals = run_all_radars()
            st.success(f"已更新 {updated} 則新聞智慧標籤，並產生 {len(signals)} 筆雷達訊號")

    with col4:
        st.metric("PIOS 總分", decision.score)
        st.caption(f"{_level_icon(decision.level)} {decision.summary}")

    with col5:
        st.metric("建議模式", decision.mode)
        st.caption(f"平常 {settings.portfolio.get('modes', {}).get('normal', '514')}｜警戒 {settings.portfolio.get('modes', {}).get('alert', '433')}")

    st.divider()

    with db_session() as session:
        source_runs = session.execute(select(SourceRun).order_by(SourceRun.started_at.desc()).limit(14)).scalars().all()
        latest_snapshots = session.execute(select(MarketSnapshot).where(MarketSnapshot.source != "mock_market").order_by(MarketSnapshot.captured_at.desc()).limit(80)).scalars().all()
        mock_snapshots = session.execute(select(MarketSnapshot).where(MarketSnapshot.source == "mock_market").order_by(MarketSnapshot.captured_at.desc()).limit(20)).scalars().all()
        latest_signals = session.execute(select(RadarSignal).order_by(RadarSignal.created_at.desc()).limit(12)).scalars().all()
        latest_news = session.execute(select(NewsItem).order_by(NewsItem.impact_score.desc().nullslast(), NewsItem.captured_at.desc()).limit(30)).scalars().all()

    a, b, c, d = st.columns(4)
    a.metric("最近資料源執行", len(source_runs))
    b.metric("最新正式資料快照", len(latest_snapshots))
    c.metric("最新雷達訊號", len(latest_signals))
    d.metric("最新新聞", len(latest_news))

    left, right = st.columns([1, 1])

    with left:
        st.subheader("資料源健康狀態")
        if source_runs:
            st.dataframe([
                {
                    "source": r.source,
                    "status": "✅ OK" if r.ok else "⚠️ Partial/Fail",
                    "count": r.count,
                    "error": r.error,
                    "finished_at": r.finished_at,
                }
                for r in source_runs
            ], use_container_width=True, hide_index=True)
        else:
            st.info("尚未執行資料源。")

        st.subheader("最新雷達訊號")
        if latest_signals:
            for r in latest_signals:
                st.write(f"**{r.radar_name}**｜{_level_icon(r.level)} {r.level}｜{r.score}")
                st.caption(r.summary)
        else:
            st.info("尚無雷達訊號。先抓資料，再執行雷達。")

        st.subheader("個人專屬新聞流")
        if latest_news:
            for n in latest_news[:10]:
                impact = n.impact_score if n.impact_score is not None else 0
                stars = "★★★★★" if impact >= 80 else "★★★★☆" if impact >= 68 else "★★★☆☆" if impact >= 55 else "★★☆☆☆"
                st.markdown(f"- **{stars}** [{n.title}]({n.url})")
                st.caption(f"{n.category or '未分類'}｜影響 {impact}｜關聯：{n.related_symbols or '待判讀'}｜{n.published_at or n.captured_at}")
                if n.summary:
                    st.caption(n.summary)
        else:
            st.info("尚無新聞。先按『抓取新聞』。Finnhub / Marketaux 可之後再加 API key。")

    with right:
        st.subheader("最新資料快照")
        if latest_snapshots:
            st.dataframe([
                {
                    "source": s.source,
                    "symbol": s.symbol,
                    "metric": s.metric,
                    "value": s.value,
                    "note": s.raw_text,
                    "captured_at": s.captured_at,
                }
                for s in latest_snapshots
            ], use_container_width=True, hide_index=True)
        else:
            st.info("尚無正式資料。")

        st.subheader("新聞資料表")
        if latest_news:
            st.dataframe([
                {
                    "source": n.source,
                    "title": n.title,
                    "publisher": n.publisher,
                    "category": n.category,
                    "impact": n.impact_score,
                    "risk": n.risk_score,
                    "related": n.related_symbols,
                    "summary": n.summary,
                    "query": n.query,
                    "published_at": n.published_at,
                }
                for n in latest_news
            ], use_container_width=True, hide_index=True)

        with st.expander("開發測試資料 mock_market"):
            if mock_snapshots:
                st.dataframe([
                    {
                        "source": s.source,
                        "symbol": s.symbol,
                        "metric": s.metric,
                        "value": s.value,
                        "captured_at": s.captured_at,
                    }
                    for s in mock_snapshots
                ], use_container_width=True, hide_index=True)
            else:
                st.caption("目前沒有 mock 資料。")


if __name__ == "__main__":
    main()
