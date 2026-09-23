from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta

import pandas as pd


def make_post(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "id": "1",
        "platform": "Instagram",
        "content_id": "content-1",
        "creator_id": "creator-1",
        "content_type": "video",
        "content_category": "tech",
        "post_date": "2025-01-15T12:00:00",
        "views": 100,
        "likes": 5,
        "shares": 2,
        "comments_count": 1,
        "follower_count": 20_000,
        "is_sponsored": "FALSE",
        "audience_age_distribution": "19-25",
        "audience_gender_distribution": "female",
        "audience_location": "BR",
    }
    row.update(overrides)
    return row


def csv_bytes(rows: list[dict[str, object]]) -> bytes:
    if not rows:
        return b""
    fields = list(rows[0])
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def frame_from_rows(rows: list[dict[str, object]]) -> pd.DataFrame:
    from analysis import load_csv

    frame, errors = load_csv(csv_bytes(rows))
    if errors:
        raise AssertionError(errors)
    assert frame is not None
    return frame


def make_cohort(
    creators: int = 5,
    posts_per_creator: int = 6,
    erv_values: list[float] | None = None,
    *,
    start: str = "2024-11-01T12:00:00",
    sponsored: bool = False,
    **overrides: object,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    started = datetime.fromisoformat(start)
    values = erv_values or [4.0] * (creators * posts_per_creator)
    for index in range(creators * posts_per_creator):
        creator = index // posts_per_creator
        erv = values[index % len(values)]
        views = 100
        interactions = int(round(erv))
        rows.append(
            make_post(
                id=f"r-{index}",
                content_id=f"c-{index}",
                creator_id=f"creator-{creator}",
                post_date=(started + timedelta(days=index % 30)).isoformat(),
                views=views,
                likes=interactions,
                shares=0,
                comments_count=0,
                is_sponsored=str(sponsored).upper(),
                **overrides,
            )
        )
    return frame_from_rows(rows)


def frame_with_target(frame: pd.DataFrame, erv: float, **overrides: object) -> pd.DataFrame:
    values: dict[str, object] = {
        "id": "target",
        "content_id": "target-content",
        "creator_id": "target-creator",
        "post_date": "2025-01-15T12:00:00",
        "views": 100,
        "likes": int(erv),
        "shares": 0,
        "comments_count": 0,
    }
    values.update(overrides)
    row = make_post(**values)
    target = frame_from_rows([row])
    return pd.concat([frame, target], ignore_index=True)


def default_scope(**overrides: object) -> dict[str, object]:
    scope: dict[str, object] = {
        "target_start": "2025-01-15",
        "target_end": "2025-01-15",
        "reference_date": "2025-01-15",
        "filters": {},
        "strict_audience": False,
        "method_version": "1.0.0",
    }
    scope.update(overrides)
    return scope


def alert_for_target(result: dict[str, object]) -> dict[str, object]:
    return next(item for item in result["alerts"] if item["source_id"] == "target")  # type: ignore[index]


def sponsorship_rows() -> pd.DataFrame:
    frames = [
        make_cohort(5, 6, [4], sponsored=False, start="2025-01-01T12:00:00"),
        make_cohort(5, 6, [8], sponsored=True, start="2025-01-01T12:00:00"),
        make_cohort(5, 6, [6], sponsored=False, start="2025-01-01T12:00:00", content_type="image"),
    ]
    frame = pd.concat(frames, ignore_index=True)
    frame["id"] = [f"s-{i}" for i in range(len(frame))]
    frame["content_id"] = [f"sc-{i}" for i in range(len(frame))]
    frame["source_row_id"] = [f"hash:s-{i}" for i in range(len(frame))]
    return frame


def concentrated_reference() -> pd.DataFrame:
    frame = make_cohort(20, 5, [2, 4, 6, 8, 10])
    frame.loc[:79, "creator_id"] = "dominant"
    for creator, start in enumerate(range(80, 100, 5), start=1):
        frame.loc[start : start + 4, "creator_id"] = f"minor-{creator}"
    return frame


def aggregate_effect_rows(
    *, creators: int = 5, before_views: int = 100, before_interactions: int = 4,
    current_views: int = 100, current_interactions: int = 8,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    periods = (
        ("before", datetime(2025, 1, 1, 12), before_views, before_interactions),
        ("now", datetime(2025, 1, 8, 12), current_views, current_interactions),
    )
    for period, started, views, interactions in periods:
        for index in range(100):
            rows.append(
                make_post(
                    id=f"{period}-{index}",
                    content_id=f"{period}-content-{index}",
                    creator_id=f"creator-{index % creators}",
                    post_date=(started + timedelta(days=index % 7)).isoformat(),
                    views=views,
                    likes=interactions,
                    shares=0,
                    comments_count=0,
                )
            )
    return frame_from_rows(rows)


def sponsorship_frequency_rows(weeks: int) -> pd.DataFrame:
    if weeks not in (1, 2):
        raise ValueError("weeks must be 1 or 2")
    rows: list[dict[str, object]] = []
    started = datetime(2025, 1, 6, 12)
    for sponsored in (False, True):
        for creator in range(5):
            for post in range(6):
                if weeks == 2:
                    week, day = post % 2, (post // 2) * 3
                else:
                    week, day = 0, (0, 1, 2, 3, 4, 6)[post]
                marker = f"{'s' if sponsored else 'o'}-{creator}-{post}"
                rows.append(
                    make_post(
                        id=marker,
                        content_id=f"content-{marker}",
                        creator_id=f"creator-{creator}",
                        post_date=(started + timedelta(days=week * 7 + day)).isoformat(),
                        likes=8 if sponsored else 4,
                        shares=0,
                        comments_count=0,
                        is_sponsored=str(sponsored).upper(),
                    )
                )
    return frame_from_rows(rows)


def monthly_sponsorship_frequency_rows(
    sponsored_days: tuple[int, ...], *, extra_april_sponsored_days: tuple[int, ...] = ()
) -> pd.DataFrame:
    if len(sponsored_days) != 6:
        raise ValueError("sponsored_days must contain six posts per creator")
    rows: list[dict[str, object]] = []
    organic_days = (1, 3, 10, 17, 24, 31)
    for sponsored, days in ((False, organic_days), (True, sponsored_days)):
        for creator in range(5):
            for post, day in enumerate(days):
                marker = f"{'s' if sponsored else 'o'}-{creator}-{post}"
                rows.append(
                    make_post(
                        id=marker,
                        content_id=f"content-{marker}",
                        creator_id=f"creator-{creator}",
                        post_date=f"2025-03-{day:02d}T12:00:00",
                        likes=8 if sponsored else 4,
                        shares=0,
                        comments_count=0,
                        is_sponsored=str(sponsored).upper(),
                    )
                )
    for creator in range(5):
        for post, day in enumerate(extra_april_sponsored_days):
            marker = f"april-s-{creator}-{post}"
            rows.append(
                make_post(
                    id=marker,
                    content_id=f"content-{marker}",
                    creator_id=f"creator-{creator}",
                    post_date=f"2025-04-{day:02d}T12:00:00",
                    likes=20,
                    shares=0,
                    comments_count=0,
                    is_sponsored="TRUE",
                )
            )
    return frame_from_rows(rows)


def driver_rows(month_deltas: list[float], *, concentrated: bool = False) -> list[dict[str, object]]:
    """Build monthly organic text targets and video peers with exact ERv deltas."""
    rows: list[dict[str, object]] = []
    for month_index, delta in enumerate(month_deltas, start=1):
        for content_type, erv in (("text", 5.0 + delta), ("video", 5.0)):
            arm = "target" if content_type == "text" else "peer"
            for index in range(30):
                if concentrated:
                    creator = f"{arm}-dominant" if index < 26 else f"{arm}-{month_index}-{index}"
                else:
                    creator = f"{arm}-{index % 10}"
                marker = f"driver-{month_index}-{content_type}-{index}"
                rows.append(
                    make_post(
                        id=marker,
                        content_id=f"content-{marker}",
                        creator_id=creator,
                        content_type=content_type,
                        content_category="tech",
                        post_date=f"2025-{month_index:02d}-{1 + index % 28:02d}T12:00:00",
                        views=10_000,
                        likes=int(round(erv * 100)),
                        shares=0,
                        comments_count=0,
                        is_sponsored="FALSE",
                    )
                )
    return rows


def duplicate_driver_context(rows: list[dict[str, object]], **overrides: object) -> list[dict[str, object]]:
    duplicated: list[dict[str, object]] = []
    for row in rows:
        copied = dict(row)
        copied.update(overrides)
        copied["id"] = f"duplicate-{row['id']}"
        copied["content_id"] = f"duplicate-{row['content_id']}"
        copied["creator_id"] = f"duplicate-{row['creator_id']}"
        duplicated.append(copied)
    return duplicated


def default_scope_all_history(rows: list[dict[str, object]]) -> dict[str, object]:
    dates = [str(row["post_date"]) for row in rows]
    return {
        "target_start": min(dates),
        "target_end": max(dates),
        "reference_date": max(dates),
        "filters": {},
        "include_post_alerts": False,
    }


def monthly_sponsorship_rows(months: int = 3) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for month in range(1, months + 1):
        for sponsored, erv in ((False, 4.0), (True, 5.0)):
            arm = "sponsored" if sponsored else "organic"
            for index in range(30):
                marker = f"finance-{month}-{arm}-{index}"
                rows.append(
                    make_post(
                        id=marker,
                        content_id=f"content-{marker}",
                        creator_id=f"{arm}-{index % 10}",
                        platform="YouTube",
                        content_type="mixed",
                        content_category="finance",
                        post_date=f"2025-{month:02d}-{1 + index % 28:02d}T12:00:00",
                        views=10_000,
                        likes=int(erv * 100),
                        shares=0,
                        comments_count=0,
                        is_sponsored=str(sponsored).upper(),
                    )
                )
    return rows
