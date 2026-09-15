#!/usr/bin/env python3
"""Download the DCCB Google Calendar iCal feed and rebuild events.json."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import recurring_ical_events
from icalendar import Calendar


TIMEZONE = ZoneInfo("Asia/Taipei")
OUTPUT = Path(__file__).resolve().parents[1] / "events.json"


def text(value: object | None) -> str:
    return "" if value is None else str(value).strip()


def local_start(value: date | datetime) -> tuple[str, str]:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=TIMEZONE)
        else:
            value = value.astimezone(TIMEZONE)
        return value.strftime("%Y-%m-%d"), value.strftime("%H:%M")
    return value.isoformat(), ""


def main() -> int:
    ical_url = os.environ.get("GOOGLE_CALENDAR_ICAL_URL", "").strip()
    if not ical_url.startswith("https://"):
        print("GOOGLE_CALENDAR_ICAL_URL is missing or is not an HTTPS URL.", file=sys.stderr)
        return 2

    request = urllib.request.Request(ical_url, headers={"User-Agent": "DCCB-calendar-sync/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        calendar = Calendar.from_ical(response.read())

    today = datetime.now(TIMEZONE).date()
    range_start = datetime(today.year - 1, 1, 1, tzinfo=TIMEZONE)
    range_end = datetime(today.year + 3, 1, 1, tzinfo=TIMEZONE)
    components = recurring_ical_events.of(calendar).between(range_start, range_end)

    events: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for component in components:
        if text(component.get("STATUS")).upper() == "CANCELLED":
            continue
        summary = text(component.get("SUMMARY"))
        start_property = component.get("DTSTART")
        if not summary or start_property is None:
            continue
        event_date, event_time = local_start(start_property.dt)
        key = (event_date, event_time, summary)
        if key in seen:
            continue
        seen.add(key)
        events.append(
            {
                "date": event_date,
                "time": event_time,
                "title": summary,
                "location": text(component.get("LOCATION")),
                "description": text(component.get("DESCRIPTION")),
            }
        )

    events.sort(key=lambda event: (event["date"], event["time"], event["title"]))
    OUTPUT.write_text(json.dumps(events, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(events)} events to {OUTPUT.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
