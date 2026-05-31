    if link and link != "暂无链接":
        return f"[**{trimmed}**]({link})"
    return f"**{trimmed}**"


def build_briefing(items: List[Dict[str, Any]], window_label: str) -> str:
    lines = [
        "以下为产业研究视角的信息整理，不构成投资建议。",
        "",
        f"## AI 行业热点简报（{window_label}）",
        "",
    ]

    for index, item in enumerate(items, start=1):
        title = text_of(item, "title", "title_en")
        summary = text_of(item, "summary", "description", "content") or "该事件来自 AIHOT 最新条目，建议结合原文进一步核验。"
        event_type = classify_event(item)
        upstream, midstream, downstream, path = impact_for(event_type)
        link = link_of(item)

        lines.extend(
            [
                f"### {index}. {title}",
                f"- 来源与时间：{source_of(item)}，{human_time(item_time(item))}",
                f"- 原文链接：{link}",
                f"- 事件类型：{event_type}",
                f"- 一句话摘要：{summary[:180]}",
                f"- 影响链条：{path}",
                "- 产业链影响：",
                f"  - 上游：{upstream}",
                f"  - 中游：{midstream}",
                f"  - 下游：{downstream}",
                f"- 推送理由：该事件与 {event_type} 相关，可能影响 AI 产业链的需求、成本、生态或监管预期。",
                "- 风险提示：自动简报仅基于公开信息和规则化判断，不能直接外推为投资结论，需继续观察原文细节、采用数据和商业化进展。",
                "",
            ]
        )

    return "\n".join(lines).strip()


def build_card_payload(item: Dict[str, Any], index: int, window_label: str) -> Dict[str, Any]:
    title = text_of(item, "title", "title_en")
    summary = text_of(item, "summary", "description", "content") or "该事件来自 AIHOT 最新条目，建议结合原文进一步核验。"
    event_type = classify_event(item)
    upstream, midstream, downstream, path = impact_for(event_type)
    link = link_of(item)
    source = source_of(item)
    published = human_time(item_time(item))

    elements: List[Dict[str, Any]] = [
        {
            "tag": "markdown",
            "content": (
                f"{markdown_title(title, link)}\n\n"
                f"{trim_text(summary, 155)}"
            ),
        },
        {"tag": "hr"},
        {
            "tag": "markdown",
            "content": (
                f"**产业链影响**\n"
                f"上游：{impact_icon(upstream)} {trim_text(upstream, 72)}\n"
                f"中游：{impact_icon(midstream)} {trim_text(midstream, 72)}\n"
                f"下游：{impact_icon(downstream)} {trim_text(downstream, 72)}"
            ),
        },
        {
            "tag": "markdown",
            "content": (
                f"**影响链条**：{trim_text(path, 95)}\n"
                f"📰 {source} · {published} · {event_type} · Top {index} · {window_label}"
            ),
        },
    ]

    return {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": "red",
                "title": {"tag": "plain_text", "content": f"🔴 AI产业链影响研判 #{index}"},
            },
            "elements": elements,
        },
    }


def fetch_with_fallback(now: datetime, min_items: int, limit: int) -> Tuple[List[Dict[str, Any]], str]:
    recent_since = now - timedelta(minutes=60)
    recent_items = fetch_items(recent_since)
    selected = select_items(recent_items, limit)
    if len(selected) >= min_items:
        return selected, "最近 60 分钟"

    fallback_since = now - timedelta(hours=24)
    fallback_items = fetch_items(fallback_since)
    selected = select_items(fallback_items, limit)
    return selected, "最近 24 小时精选"


def push_payload_to_feishu(webhook_url: str, payload: Dict[str, Any]) -> None:
    data = http_json(webhook_url, method="POST", payload=payload)
    if isinstance(data, dict) and data.get("StatusCode") not in (None, 0):
        raise RuntimeError(f"Feishu webhook returned an error: {data}")
    if isinstance(data, dict) and data.get("code") not in (None, 0):
        raise RuntimeError(f"Feishu webhook returned an error: {data}")


def push_text_to_feishu(webhook_url: str, text: str) -> None:
    payload = {"msg_type": "text", "content": {"text": text}}
    push_payload_to_feishu(webhook_url, payload)


def push_cards_to_feishu(webhook_url: str, items: List[Dict[str, Any]], window_label: str) -> None:
    for index, item in enumerate(items, start=1):
        push_payload_to_feishu(webhook_url, build_card_payload(item, index, window_label))


def main() -> int:
    parser = argparse.ArgumentParser(description="Push AIHOT industry briefing to Feishu.")
    parser.add_argument("--dry-run", action="store_true", help="Print the briefing instead of sending it.")
    parser.add_argument("--limit", type=int, default=3, help="Maximum number of items to include.")
    parser.add_argument("--min-items", type=int, default=3, help="Fallback to 24h when recent items are below this count.")
    parser.add_argument(
        "--message-format",
        choices=("card", "text"),
        default="card",
        help="Feishu message format. Card is the default mobile-friendly style.",
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    try:
        webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
        if not args.dry_run and not webhook_url:
            print("FEISHU_WEBHOOK_URL is not configured.", file=sys.stderr)
            return 2

        items, window_label = fetch_with_fallback(now, args.min_items, args.limit)
        if not items:
            print("No relevant AIHOT items found; skip Feishu push.")
            return 0

        if args.dry_run:
            if args.message_format == "card":
                payloads = [build_card_payload(item, index, window_label) for index, item in enumerate(items, start=1)]
                print(json.dumps(payloads, ensure_ascii=False, indent=2))
            else:
                print(build_briefing(items, window_label=window_label))
            return 0

        if args.message_format == "card":
            push_cards_to_feishu(webhook_url, items, window_label)
            print(f"Pushed {len(items)} AIHOT card messages to Feishu.")
        else:
            push_text_to_feishu(webhook_url, build_briefing(items, window_label=window_label))
            print(f"Pushed {len(items)} AIHOT items to Feishu.")
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
