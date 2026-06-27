from __future__ import annotations

from radars.base import RadarResult


class ChengxinWatchRadar:
    name = "chengxin_watch"

    def evaluate(self) -> list[RadarResult]:
        # v0.2 先建立雷達位置；v0.3 接公開資訊觀測站與法人資料後正式啟用。
        return [
            RadarResult(
                radar_name=self.name,
                level="watch",
                score=50,
                summary="成信 6969 追蹤雷達已建立：等待接入公告、法人、融資與產能資料。",
            )
        ]
