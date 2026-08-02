from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch

from marketing import zernio


class ZernioDedupeTests(unittest.TestCase):
    def test_existing_today_post_matches_platform_day(self) -> None:
        posts = [
            {
                "_id": "post-fb",
                "content": "Today at Sacred Ground — Example.",
                "status": "published",
                "publishedAt": "2026-08-02T13:14:17.645Z",
                "platforms": [
                    {
                        "platform": "facebook",
                        "accountId": {"_id": "acct-fb"},
                        "status": "published",
                    }
                ],
            },
            {
                "_id": "post-ig",
                "content": "Today at Sacred Ground — Example.",
                "status": "published",
                "publishedAt": "2026-08-02T13:14:19.095Z",
                "platforms": [
                    {
                        "platform": "instagram",
                        "accountId": "acct-ig",
                        "status": "published",
                    }
                ],
            },
        ]
        with patch.object(zernio, "configured", return_value=True), patch.object(
            zernio, "list_posts", return_value=posts
        ):
            hit = zernio.existing_today_post(
                platform="facebook",
                account_id="acct-fb",
                day=date(2026, 8, 2),
            )
            self.assertEqual(hit["_id"], "post-fb")
            miss = zernio.existing_today_post(
                platform="facebook",
                account_id="acct-fb",
                day=date(2026, 8, 1),
            )
            self.assertIsNone(miss)
            other = zernio.existing_today_post(
                platform="instagram",
                account_id="acct-ig",
                day=date(2026, 8, 2),
            )
            self.assertEqual(other["_id"], "post-ig")
