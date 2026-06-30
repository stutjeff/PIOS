from __future__ import annotations

import json
import streamlit as st
from sqlalchemy import select

from core.settings import load_settings
from data_sources.manager import build_default_manager
from radars.decision import latest_pios_decision
from services.news_ingestion import build_default_news_manager
from services.news_intelligence import enrich_recent_news
from services.radar_runner import run_all_radars
from services.alerts import generate_alerts
from services.exporter import table_to_frame
from storage.db import init_db, db_session
from storage.models import AlertEvent, MarketSnapshot, NewsItem, PiosScoreHistory, RadarSignal, SourceRun


def _level_icon(level: str) -> str:
    return {"green": "🟢", "yellow": "🟡", "red": "🔴", "gray": "⚪", "watch": "⚪"}.get(level, "⚪")


def _stars(score: float | None) -> str:
    s = float(score or 0)
    return "★★★★★" if s >= 80 else "★★★★☆" if s >= 68 else "★★★☆☆" if s >= 55 else "★★☆☆☆"


def _run_full_cycle() -> None:
    market = build_default_manager().fetch_all()
    news = build_default_news_manager().fetch_all()
    enriched = enrich_recent_news(limit=240)
    signals = run_all_radars()
    alerts = generate_alerts()
    st.success(f"全系統完成：市場 {sum(r.count for r in market)} 筆｜新聞新增 {sum(r.count for r in news)} 則｜智慧化 {enriched} 則｜雷達 {len(signals)} 筆｜警報 {alerts} 筆")


def _load_dashboard_data():
    with db_session() as session:
        source_runs = session.execute(select(SourceRun).order_by(SourceRun.started_at.desc()).limit(20)).scalars().all()
        latest_snapshots = session.execute(select(MarketSnapshot).where(MarketSnapshot.source != "mock_market").order_by(MarketSnapshot.captured_at.desc()).limit(120)).scalars().all()
        mock_snapshots = session.execute(select(MarketSnapshot).where(MarketSnapshot.source == "mock_market").order_by(MarketSnapshot.captured_at.desc()).limit(20)).scalars().all()
        latest_signals = session.execute(select(RadarSignal).order_by(RadarSignal.created_at.desc()).limit(20)).scalars().all()
        latest_news = session.execute(select(NewsItem).order_by(NewsItem.impact_score.desc().nullslast(), NewsItem.captured_at.desc()).limit(50)).scalars().all()
        alerts = session.execute(select(AlertEvent).order_by(AlertEvent.created_at.desc()).limit(20)).scalars().all()
        score_history = session.execute(select(PiosScoreHistory).order_by(PiosScoreHistory.created_at.desc()).limit(30)).scalars().all()
    return source_runs, latest_snapshots, mock_snapshots, latest_signals, latest_news, alerts, score_history


def main() -> None:
    settings = load_settings()
    st.set_page_config(page_title=settings.app.name, layout="wide")
    init_db()

    st.title("PIOS 4.0 Enterprise")
    st.caption("資料源、新聞、雷達、規則、紀律。UI 是駕駛艙，不是把引擎綁死在方向盤上。")

    decision = latest_pios_decision()

    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        if st.button("全系統更新", type="primary"):
            _run_full_cycle()
            decision = latest_pios_decision()
    with c2:
        if st.button("抓取市場資料"):
            results = build_default_manager().fetch_all()
            st.success(f"市場資料源完成：成功 {sum(1 for r in results if r.ok)}，異常 {sum(1 for r in results if not r.ok)}")
            for r in results:
                st.write(("✅" if r.ok else "⚠️") + f" {r.source}: {r.count} 筆" + (f"｜{r.error}" if r.error else ""))
    with c3:
        if st.button("抓取新聞"):
            results = build_default_news_manager().fetch_all()
            updated = enrich_recent_news(limit=240)
            st.success(f"新聞資料源完成：成功 {sum(1 for r in results if r.ok)}，異常 {sum(1 for r in results if not r.ok)}；智慧化 {updated} 則")
            for r in results:
                st.write(("✅" if r.ok else "⚠️") + f" {r.source}: 新增 {r.count} 則" + (f"｜{r.error}" if r.error else ""))
    with c4:
        if st.button("執行雷達 / 產生警報"):
            updated = enrich_recent_news(limit=240)
            signals = run_all_radars()
            alerts = generate_alerts()
            decision = latest_pios_decision(save_history=True)
            st.success(f"已更新 {updated} 則新聞智慧標籤，產生 {len(signals)} 筆雷達訊號、{alerts} 筆警報")

    st.divider()

    source_runs, latest_snapshots, mock_snapshots, latest_signals, latest_news, alerts, score_history = _load_dashboard_data()
    decision = latest_pios_decision()

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("PIOS 壓力分", decision.score)
    k2.metric("建議模式", decision.mode)
    k3.metric("資料源執行", len(source_runs))
    k4.metric("正式資料快照", len(latest_snapshots))
    k5.metric("雷達訊號", len(latest_signals))
    k6.metric("新聞", len(latest_news))
    st.caption(f"{_level_icon(decision.level)} {decision.summary}")

    tab_dash, tab_news, tab_radar, tab_data, tab_export = st.tabs(["作戰總覽", "新聞中心", "雷達與分數", "資料健康", "匯出/設定"])

    with tab_dash:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("警報中心")
            if alerts:
                for a in alerts[:8]:
                    st.write(f"**{_level_icon(a.level)} {a.title}**")
                    st.caption(f"{a.detail or ''}｜{a.created_at}")
            else:
                st.info("尚無警報。")

            st.subheader("個人專屬新聞流")
            if latest_news:
                for n in latest_news[:8]:
                    st.markdown(f"- **{_stars(n.impact_score)}** [{n.title}]({n.url})")
                    st.caption(f"{n.category or '未分類'}｜影響 {n.impact_score or 0}｜風險 {n.risk_score or 0}｜關聯：{n.related_symbols or '待判讀'}｜{n.published_at or n.captured_at}")
                    if n.summary:
                        st.caption(n.summary)
            else:
                st.info("尚無新聞。先按『抓取新聞』。")
        with right:
            st.subheader("PIOS 分數拆解")
            if decision.components:
                st.dataframe([
                    {"雷達": c.name, "壓力分": c.score, "燈號": f"{_level_icon(c.level)} {c.level}", "權重": c.weight, "摘要": c.summary}
                    for c in decision.components
                ], use_container_width=True, hide_index=True)
            else:
                st.info("尚無雷達結果。")

            st.subheader("最新資料快照")
            if latest_snapshots:
                st.dataframe([
                    {"source": s.source, "symbol": s.symbol, "metric": s.metric, "value": s.value, "note": s.raw_text, "captured_at": s.captured_at}
                    for s in latest_snapshots[:30]
                ], use_container_width=True, hide_index=True)
            else:
                st.info("尚無正式資料。")

    with tab_news:
        st.subheader("新聞資料表")
        if latest_news:
            category = st.selectbox("分類篩選", ["全部"] + sorted({n.category or "未分類" for n in latest_news}))
            filtered = [n for n in latest_news if category == "全部" or (n.category or "未分類") == category]
            st.dataframe([
                {"星級": _stars(n.impact_score), "title": n.title, "publisher": n.publisher, "category": n.category, "impact": n.impact_score, "risk": n.risk_score, "related": n.related_symbols, "summary": n.summary, "query": n.query, "published_at": n.published_at, "url": n.url}
                for n in filtered
            ], use_container_width=True, hide_index=True)
        else:
            st.info("尚無新聞。")

    with tab_radar:
        st.subheader("最新雷達訊號")
        if latest_signals:
            for r in latest_signals:
                st.write(f"**{r.radar_name}**｜{_level_icon(r.level)} {r.level}｜{r.score}")
                st.caption(r.summary)
        else:
            st.info("尚無雷達訊號。")

        st.subheader("PIOS 壓力分歷史")
        if score_history:
            hist = list(reversed(score_history))
            st.line_chart({"PIOS壓力分": [h.score for h in hist]})
            st.dataframe([
                {"created_at": h.created_at, "score": h.score, "level": h.level, "mode": h.mode, "summary": h.summary}
                for h in score_history
            ], use_container_width=True, hide_index=True)

    with tab_data:
        st.subheader("資料源健康狀態")
        if source_runs:
            st.dataframe([
                {"source": r.source, "status": "✅ OK" if r.ok else "⚠️ Partial/Fail", "count": r.count, "error": r.error, "finished_at": r.finished_at}
                for r in source_runs
            ], use_container_width=True, hide_index=True)
        with st.expander("開發測試資料 mock_market"):
            if mock_snapshots:
                st.dataframe([{ "source": s.source, "symbol": s.symbol, "metric": s.metric, "value": s.value, "captured_at": s.captured_at } for s in mock_snapshots], use_container_width=True, hide_index=True)
            else:
                st.caption("目前沒有 mock 資料。")

    with tab_export:
        st.subheader("資料匯出")
        table = st.selectbox("選擇資料表", ["market_snapshots", "news_items", "radar_signals", "source_runs", "pios_score_history", "alert_events"])
        df = table_to_frame(table, limit=800)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("下載 CSV", df.to_csv(index=False).encode("utf-8-sig"), file_name=f"{table}.csv", mime="text/csv")
        st.subheader("設定摘要")
        st.json(json.loads(settings.model_dump_json()))


if __name__ == "__main__":
    main()
