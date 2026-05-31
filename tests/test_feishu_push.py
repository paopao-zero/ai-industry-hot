import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from scripts import feishu_push


class FeishuPushTests(unittest.TestCase):
    def test_normalize_items_accepts_common_response_shapes(self):
        self.assertEqual(feishu_push.normalize_items([{"title": "A"}]), [{"title": "A"}])
        self.assertEqual(feishu_push.normalize_items({"items": [{"title": "B"}]}), [{"title": "B"}])
        self.assertEqual(feishu_push.normalize_items({"data": [{"title": "C"}, "skip"]}), [{"title": "C"}])
        self.assertEqual(feishu_push.normalize_items({"unknown": []}), [])

    def test_parse_time_handles_utc_and_fractional_seconds(self):
        parsed = feishu_push.parse_time("2026-05-31T12:34:56.123456789Z")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.tzinfo, timezone.utc)
        self.assertEqual(parsed.microsecond, 123456)

    def test_select_items_deduplicates_by_link_and_prefers_scored_recent_items(self):
        old = "2026-05-30T00:00:00Z"
        recent = "2026-05-31T00:00:00Z"
        items = [
            {"title": "普通新闻", "url": "https://example.com/a", "publishedAt": recent},
            {"title": "NVIDIA GPU 数据中心更新", "url": "https://example.com/b", "publishedAt": old},
            {"title": "重复标题", "url": "https://example.com/b", "publishedAt": recent},
        ]

        selected = feishu_push.select_items(items, limit=2)

        self.assertEqual([item["url"] for item in selected], ["https://example.com/b", "https://example.com/a"])

    def test_build_card_payload_contains_core_fields(self):
        payload = feishu_push.build_card_payload(
            {
                "title": "OpenAI 发布新模型",
                "summary": "用于测试的摘要",
                "url": "https://example.com/news",
                "publishedAt": "2026-05-31T00:00:00Z",
                "source": "Example",
            },
            index=1,
            window_label="最近 60 分钟",
        )

        self.assertEqual(payload["msg_type"], "interactive")
        content = "\n".join(element.get("content", "") for element in payload["card"]["elements"])
        self.assertIn("产业链影响", content)
        self.assertIn("OpenAI 发布新模型", content)
        self.assertIn("最近 60 分钟", content)

    def test_fetch_with_fallback_uses_24h_when_recent_items_are_insufficient(self):
        now = datetime(2026, 5, 31, tzinfo=timezone.utc)
        recent_item = {
            "title": "近期条目",
            "url": "https://example.com/recent",
            "publishedAt": (now - timedelta(minutes=10)).isoformat(),
        }
        fallback_item = {
            "title": "NVIDIA GPU 重要进展",
            "url": "https://example.com/fallback",
            "publishedAt": (now - timedelta(hours=2)).isoformat(),
        }

        with patch.object(feishu_push, "fetch_items", side_effect=[[recent_item], [recent_item, fallback_item]]) as fetch_items:
            items, label = feishu_push.fetch_with_fallback(now, min_items=2, limit=2)

        self.assertEqual(label, "最近 24 小时精选")
        self.assertEqual(len(items), 2)
        self.assertEqual(fetch_items.call_count, 2)


if __name__ == "__main__":
    unittest.main()
