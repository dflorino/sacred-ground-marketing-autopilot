# Marketing Autopilot — API Contract (v1)

*Phase 1 · drafts-first · Version 1.0*

## Read this first

Marketing Autopilot turns WordPress events into **social draft packages**.  
It does **not** publish in Phase 1. Publishing is gated by phase + approval + pause.

## Draft package

```json
{
  "id": "sgma-20260709-today-fb-a1b2c3",
  "version": "1.0",
  "campaign": "today",
  "platform": "facebook",
  "status": "draft",
  "approval_status": "pending",
  "fingerprint": "today|2026-07-09|facebook|412,415",
  "created_at": "2026-07-09T17:00:00-07:00",
  "timezone": "America/Chicago",
  "schedule_recommendation": {
    "recommended_at": "2026-07-09T09:00:00-05:00",
    "rationale": "Morning shop-open window for same-day foot traffic"
  },
  "caption": { "text": "...", "hashtags": ["#SacredGround", "#ArlingtonHeights"] },
  "image": {
    "source": "event_featured",
    "url": "https://...",
    "event_id": 412,
    "prompt": null,
    "recommendation": "Use Holistic Fair featured image as-is"
  },
  "events": [
    {
      "id": 412,
      "title": "Holistic Fair",
      "start_date": "2026-07-09 10:00:00",
      "end_date": "2026-07-09 16:00:00",
      "url": "https://shopsacredground.com/event/...",
      "categories": ["Special Event"],
      "tags": [],
      "featured": true,
      "image_url": "https://..."
    }
  ],
  "links": ["https://shopsacredground.com/event/..."],
  "phase": 1,
  "publish_blocked_reason": "phase_1_drafts_only"
}
```

## Status values

| Field | Values |
|---|---|
| `status` | `draft` · `approved` · `scheduled` · `posted` · `skipped` · `rejected` |
| `approval_status` | `pending` · `approved` · `rejected` · `overridden` |

## HTTP (local)

| Endpoint | Returns |
|---|---|
| `GET /health` | liveness |
| `GET /api/v1/summary` | draft counts + pause/phase |
| `GET /api/v1/drafts` | draft list (`?status=`) |
| `GET /api/v1/drafts/{id}` | one draft |
| `POST` / mutating | **405** in Phase 1 HTTP (use CLI for approve/pause) |

## Fingerprint

`{campaign}|{date_key}|{platform}|{sorted_event_ids}`

Duplicates are refused. Posted fingerprints live in `data/state/posted.json`.
