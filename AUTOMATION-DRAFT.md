# Automation draft (NOT activated)

Daily Today posts for Sacred Ground Marketing Autopilot (Phase 2 + today auto_publish).

**Status: code ready for Today auto-approve; daily Cloud Agent publish still needs GitHub + Automation.**

## Image rules (locked)

| Situation | Image used |
|-----------|------------|
| Exactly **one** today event **with** a featured photo | That event’s featured image |
| Multi-event day, or one event with no photo | Store **exterior** (`Screenshot-2026-03-05-at-9.20.15-AM.png`) |
| **Empty calendar** | Store exterior + visit/brand caption |

Interior kept on file: `CD3C3C2E-620B-4933-BC24-11ED63552132-1.png` (not the auto-publish fallback).

Never post without a real media URL. Never AI-generate a mystery image for auto-publish.

Empty-day caption: “Visit Sacred Ground for cool and unusual things” / Chicagoland’s most famous crystal shop.

## Requirements reflected

1. Schedule: **7:00 AM America/Chicago**
2. Live WordPress events only (`live-strict`)
3. Repo must be on GitHub for Cloud Agent checkout
4. WordPress refresh failure → **zero new drafts** + clear error report (no stale cache)
5. Never overwrite edited / approved / rejected / reviewed drafts
6. **Today** campaign: `auto_publish=true` (auto-approves in Phase 2+). Week/spotlight still need human approve.

## Proposed configuration

| Draft field | Value |
|-------------|------------------------------|
| Name / description | **SG Marketing Autopilot Daily** — Every day at 7:00 AM America/Chicago, pull live Sacred Ground WordPress / The Events Calendar events and create Phase 1 social drafts (today / week / spotlight) for Facebook and Instagram. Never publish. |
| Trigger | Every day at **7:00 AM America/Chicago** |
| Tools | Cloud Agent + repo checkout. Use live TEC REST: `https://shopsacredground.com/wp-json/tribe/events/v1/events`. Do not rely on stale `data/cache`. |
| Instructions | See prompt below. |
| Resolved settings | Schedule timezone: **America/Chicago**. Source: `live-strict`. Phase: 1. |
| To finish in editor | (1) Set schedule to 7:00 AM with timezone **America/Chicago** in the Automations UI — do not bake a UTC-only cron as a substitute. (2) Select the GitHub repo once it exists. (3) Confirm Cloud Agent network can reach shopsacredground.com. (4) Do not enable publish/schedule actions. |

### Agent instructions (proposed)

```
You are running Sacred Ground Marketing Autopilot in Phase 1 (drafts only).

Hard rules:
1. Schedule context is America/Chicago. Event times and shop-local post times are America/Chicago.
2. Refresh events from live WordPress / The Events Calendar only:
   https://shopsacredground.com/wp-json/tribe/events/v1/events
   Run: python3 -m marketing run --source live-strict
3. If the WordPress/TEC refresh fails for any reason: create NO new drafts, do not read or use data/cache/live_events.json or fixtures, and report a clear failure with error wordpress_refresh_failed.
4. Never overwrite or recreate a draft that is edited, approved, rejected, skipped, locked, or otherwise reviewed. Fingerprints that already exist must be left alone.
5. Phase is 1: never call social_publish, never schedule live posts, even if a draft is approved. Approval only updates review status.
6. After a successful run, summarize the review queue (campaign, platform, event titles, schedule recommendation, image source). Do not publish.
```

## Verification checklist (current status)

| Requirement | Status |
|-------------|--------|
| 1. Schedule America/Chicago | Reflected in this proposal. Must be set in Automations UI timezone (not converted to UTC here). |
| 2. Cloud Agent → live WordPress | **Partially confirmed.** Live events are reachable via Sacred Ground WordPress (WP-CLI/MCP confirmed). Public TEC REST is the intended Cloud Agent source. Outbound HTTPS from *this* local agent session is blocked by sandbox, so Cloud Agent reachability must be confirmed on first dry run after activation. |
| 3. Repo on GitHub | **Not ready.** `~/Projects/sacred-ground-marketing-autopilot` is local only — git is not fully initialized and there is no GitHub remote. Cloud Agent cannot check it out until the repo is pushed. |
| 4. Fail hard on WP refresh | **Implemented** in code: `live-strict` + `wordpress_refresh_failed` returns zero drafts. |
| 5. No overwrite of reviewed drafts | **Implemented** in code: fingerprint block + save/update guards. |
| 6. No Phase 1 publish | **Implemented** in code: `phase_1_drafts_only` even after approve. |

## Blockers before activation

1. Initialize git and push `sacred-ground-marketing-autopilot` to GitHub under an account Cloud Agent can access.
2. Confirm Automations schedule UI is set to **7:00 AM America/Chicago** (not Phoenix, not a silent UTC substitute).
3. Optional but recommended: one Cloud Agent dry run that only hits TEC REST and reports success/failure — still without activating the daily schedule.


## Daily week-ahead (proposed)

| Field | Value |
|---|---|
| Name | **SG Marketing Week-Ahead** |
| Trigger | Every day at **7:00 PM America/Chicago** |
| Command | `python3 -m marketing run --source live-strict` (week_ahead drafts) |
| Platforms | Facebook + Instagram |
| Art | Store interior composite + darker translucent logo |
| Phase | 1 drafts until Founder approves Phase 2 publish |
