# Automation draft — SG Today 7am Social (LIVE)

Daily Today posts for Sacred Ground Marketing Autopilot.

**Status: auto_publish ON.** Every morning at 7:00 AM America/Chicago: generate Today FB+IG and publish via Zernio.

## Image rules (locked)

| Situation | Image used |
|-----------|------------|
| Specialty match (tarot, reiki, etc.) | Rule library URL (7-day no-repeat) |
| Multi-event / no specialty | Store exterior or rotation rules |
| **Empty calendar** | Store exterior + visit/brand caption |

Never post without a real media URL.

## Daily commands (Cloud Agent)

```bash
python3 -m marketing run --source live-strict
python3 -m marketing publish-today
```

Secret required: **`ZERNIO_API_KEY`** (Cursor Cloud Agent secrets).

## Agent instructions

```
You are running Sacred Ground Marketing Autopilot for the daily Today campaign.

Hard rules:
1. Timezone context is America/Chicago. Shop-local post time is 7:00 AM America/Chicago.
2. Checkout this repo and run from the project root.
3. Refresh live WordPress / The Events Calendar only:
   python3 -m marketing run --source live-strict
4. If the WordPress/TEC refresh fails: create NO new drafts, do not use stale cache, report wordpress_refresh_failed, and STOP. Do not publish.
5. Never overwrite or recreate a draft that is edited, approved, rejected, skipped, locked, or otherwise reviewed. Fingerprints that already exist must be left alone.
6. Today campaign has auto_publish=true. After a successful live-strict run, publish today's posts:
   python3 -m marketing publish-today
   This uses ZERNIO_API_KEY from Cloud Agent secrets. Do not skip publish unless step 4 failed or the key is missing.
7. Only Facebook + Instagram Today posts. Do not publish week / week_ahead / spotlight.
8. After the run, summarize: events (or empty-day visit), platforms, image URL/rule, publish results (posted/scheduled/errors). Include Zernio post links when available.
```

## Editor checklist

1. Name: **SG Today 7am Social**
2. Schedule: **7:00 AM** · timezone **America/Chicago**
3. Repo: `dflorino/sacred-ground-marketing-autopilot` · branch `main`
4. Secret: `ZERNIO_API_KEY`
5. Only **one** Active automation at 7am (disable duplicates)
6. Status: **Active**
