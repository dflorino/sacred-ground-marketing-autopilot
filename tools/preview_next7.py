#!/usr/bin/env python3
"""Dry-run preview of morning / afternoon / night plates for the next N days.

Plans images exactly like the pipeline does (same classify + plan_image calls)
but never records usage and never writes drafts. Simulated usage carries across
days so the preview shows the real never-reuse rotation.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marketing import classify, images, schedule  # noqa: E402
from marketing.ingest import load_events, tzinfo  # noqa: E402
from marketing.paths import settings  # noqa: E402


def plan_day(events, day, as_of, used):
    cfg = settings()
    out = {"date": day.isoformat(), "weekday": day.strftime("%A")}

    combined_morning, tomorrow_events, publish_day_events, event_day = (
        classify.morning_lineup_events(events, day, after=as_of)
    )
    from marketing import celestial as cel_mod

    cel_morning_hit = cel_mod.celestial_morning_for(day)
    flyer_day = day if (publish_day_events or cel_morning_hit) else event_day
    morning_events = classify.cap_events(
        combined_morning, int(cfg.get("max_today_events_in_caption") or 8)
    )
    m = images.plan_image(
        morning_events,
        "today",
        day=flyer_day,
        platform="facebook",
        exclude_urls=sorted(used),
    )
    # Pipeline override: a Founder-locked date-keyed flyer wins over any rule pick.
    from marketing import morning_flyers as mf
    from marketing.models import ImagePlan

    locked_url = mf.founder_approved_flyer_url(flyer_day, "facebook")
    if locked_url:
        m = ImagePlan(
            source="morning_flyer",
            url=locked_url,
            event_id=m.event_id,
            recommendation=f"Founder-locked morning flyer for {flyer_day.isoformat()}",
            rule="morning_flyer",
            prebranded=True,
        )
    out["morning"] = slot(m, morning_events, schedule.schedule_today(day))
    out["morning"]["flyer_day"] = flyer_day.isoformat()
    if m.url:
        used.add(str(m.url))

    spotlight_ev = classify.pick_afternoon_spotlight(events, day, after=as_of)
    af_events = [spotlight_ev] if spotlight_ev else []
    a = images.plan_image(
        af_events,
        "afternoon_spotlight",
        day=day,
        platform="facebook",
        exclude_urls=sorted(used),
    )
    out["afternoon"] = slot(a, af_events, schedule.schedule_afternoon_spotlight(day))
    if a.url:
        used.add(str(a.url))

    ahead_events, window_start, horizon = classify.week_ahead_lineup_events(
        events,
        day,
        after=as_of,
        max_events=int(cfg.get("max_week_ahead_events_in_caption") or 8),
    )
    n = images.plan_image(
        ahead_events,
        "week_ahead",
        day=day,
        platform="facebook",
        exclude_urls=sorted(used),
    )
    out["night"] = slot(n, ahead_events, schedule.schedule_week_ahead(day))
    out["night"]["window"] = f"{window_start.isoformat()} +{horizon}d"
    if n.url:
        used.add(str(n.url))

    return out


def slot(plan, events, sched):
    when = ""
    if isinstance(sched, dict):
        when = str(sched.get("at") or sched.get("scheduled_at") or "")
    else:
        when = str(sched)
    return {
        "url": plan.url or "",
        "rule": plan.rule or "",
        "source": plan.source or "",
        "prebranded": bool(plan.prebranded),
        "recommendation": plan.recommendation or "",
        "events": [e.title for e in events],
        "schedule": when,
    }


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    events, source = load_events("auto")
    as_of = datetime.now(tzinfo())
    start = as_of.date()
    valid, _ = classify.filter_valid(events, on=start)

    used = set(images.urls_ever_used())
    rows = [plan_day(valid, start + timedelta(days=i), as_of, used) for i in range(days)]
    print(json.dumps({"source": source, "start": start.isoformat(), "days": rows}, indent=2))


if __name__ == "__main__":
    main()
