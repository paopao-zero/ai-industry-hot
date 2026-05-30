#!/usr/bin/env python3
"""Fetch AIHOT items and push a compact industry-chain briefing to Feishu."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib import parse, request
from urllib.error import HTTPError, URLError


AIHOT_ITEMS_URL = "https://aihot.virxact.com/api/public/items"
USER_AGENT = "Mozilla/5.0 (compatible; ai-industry-hot/1.0)"
BEIJING_TZ = timezone(timedelta(hours=8))


EVENT_KEYWORDS = [
    ("模型发布", ["model", "gpt", "claude", "gemini", "llama", "qwen", "deepseek", "多模态", "推理", "模型"]),
    ("产品发布", ["assistant", "copilot", "app", "search", "office", "产品", "助手", "搜索"]),
    ("算力硬件", ["gpu", "nvidia", "h100", "b200", "gb200", "芯片", "算力", "数据中心", "服务器"]),
    ("云服务", ["cloud", "api", "azure", "aws", "google cloud", "云", "平台"]),
    ("Agent应用", ["agent", "mcp", "workflow", "browser", "coding", "智能体", "代理"]),
    ("投融资并购", ["funding", "investment", "acquisition", "ipo", "融资", "并购", "投资", "估值"]),
    ("政策监管", ["regulation", "copyright", "safety", "policy", "监管", "政策", "版权", "安全"]),
    ("开源生态", ["open source", "github", "hugging face", "开源", "框架", "数据集"]),
    ("论文技术突破", ["paper", "arxiv", "research", "论文", "研究", "突破"]),
]


def http_json(url: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Any:
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail[:300]}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error while requesting {url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from {url}") from exc


def fetch_items(since: datetime, take: int = 50) -> List[Dict[str, Any]]:
    params = {
        "mode": "selected",
        "since": since.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "take": str(take),
    }
    url = f"{AIHOT_ITEMS_URL}?{parse.urlencode(params)}"
    data = http_json(url)
    return normalize_items(data)


def normalize_items(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        raw_items = data
    elif isinstance(data, dict):
        for key in ("items", "data", "results", "list"):
            value = data.get(key)
            if isinstance(value, list):
                raw_items = value
                break
        else:
            raw_items = []
    else:
        raw_items = []

    return [item for item in raw_items if isinstance(item, dict)]


def parse_time(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def item_time(item: Dict[str, Any]) -> Optional[datetime]:
    for key in ("publishedAt", "published_at", "createdAt", "created_at", "time", "date"):
        parsed = parse_time(item.get(key))
        if parsed:
            return parsed
    return None


def human_time(dt: Optional[datetime]) -> str:
    if not dt:
        return "时间未知"

    now = datetime.now(BEIJING_TZ)
    local = dt.astimezone(BEIJING_TZ)
    delta = now - local
    if timedelta(0) <= delta < timedelta(hours=1):
        minutes = max(1, int(delta.total_seconds() // 60))
        return f"{minutes} 分钟前"
    if timedelta(0) <= delta < timedelta(days=1):
        hours = max(1, int(delta.total_seconds() // 3600))
        return f"{hours} 小时前"
    if local.date() == now.date():
        return f"今天 {local:%H:%M}"
    if local.date() == (now - timedelta(days=1)).date():
        return f"昨天 {local:%H:%M}"
    return f"{local.month}/{local.day} {local:%H:%M}"


def text_of(item: Dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def source_of(item: Dict[str, Any]) -> str:
    source = text_of(item, "source", "sourceName", "site", "author")
    return source or "AIHOT"


def link_of(item: Dict[str, Any]) -> str:
    return text_of(item, "url", "link", "sourceUrl", "originalUrl") or "暂无链接"


def classify_event(item: Dict[str, Any]) -> str:
    content = " ".join(
        [
            text_of(item, "title", "title_en", "summary", "description", "content"),
            " ".join(str(tag) for tag in item.get("tags", []) if isinstance(tag, str)),
            text_of(item, "category"),
        ]
    ).lower()
    for event_type, keywords in EVENT_KEYWORDS:
        if any(keyword.lower() in content for keyword in keywords):
            return event_type
    return "行业动态"


def impact_for(event_type: str) -> Tuple[str, str, str, str]:
    mapping = {
        "模型发布": (
            "算力与云基础设施，偏利好，训练和推理需求可能增加",
            "基础模型与 API 平台，偏利好，模型能力和生态竞争可能增强",
            "AI 应用与开发者工具，待观察，需验证真实采用率和成本结构",
            "模型能力变化 -> API/应用能力扩展 -> 产业链需求与竞争格局变化",
        ),
        "产品发布": (
            "暂无明确影响",
            "云服务与模型平台，待观察，取决于产品调用量和商业化节奏",
            "办公、教育、内容生成或企业服务，偏利好，应用场景可能扩大",
            "产品落地 -> 用户场景扩展 -> 下游应用活跃度变化",
        ),
        "算力硬件": (
            "GPU、AI 芯片、服务器、网络和电力配套，偏利好，算力需求信号更直接",
            "云厂商与模型平台，待观察，取决于供给节奏和采购成本",
            "AI 应用，待观察，算力成本变化可能影响推理价格",
            "硬件/数据中心变化 -> 算力供需变化 -> 模型训练和推理成本变化",
        ),
        "云服务": (
            "数据中心、服务器和网络设备，偏利好，云端 AI 服务可能带来增量需求",
            "云厂商、API 平台和 MLOps，偏利好，平台生态可能增强",
            "企业 AI 应用，偏利好，部署门槛可能下降",
            "云服务升级 -> 开发和部署门槛降低 -> 企业应用扩散",
        ),
        "Agent应用": (
            "暂无明确影响",
            "开发者工具、模型 API 和工作流平台，偏利好，工具调用和编排需求可能增加",
            "企业自动化、编码和办公场景，偏利好，效率型应用可能扩张",
            "Agent 能力增强 -> 工作流自动化 -> 企业软件和开发者生态变化",
        ),
        "投融资并购": (
            "暂无明确影响",
            "相关赛道公司和平台生态，待观察，资本投入可能加速产品化",
            "下游商业化场景，待观察，需看资金是否转化为收入和用户增长",
            "资本事件 -> 资源投入和竞争格局变化 -> 商业化进度待验证",
        ),
        "政策监管": (
            "暂无明确影响",
            "模型、云平台和数据服务，偏利空或待观察，合规成本可能上升",
            "AI 应用，待观察，取决于政策细则和执行力度",
            "监管变化 -> 合规成本和业务边界变化 -> 行业扩张节奏调整",
        ),
        "开源生态": (
            "暂无明确影响",
            "开源模型、框架和开发者生态，偏利好，创新和采用门槛可能下降",
            "AI 应用开发，偏利好，原型和落地速度可能提升",
            "开源供给增加 -> 开发门槛下降 -> 生态活跃度提升",
        ),
        "论文技术突破": (
            "暂无明确影响",
            "模型、算法和基础设施，待观察，需验证工程化可行性",
            "应用侧，待观察，短期商业影响通常不确定",
            "研究进展 -> 工程化验证 -> 产品和成本影响仍需观察",
        ),
    }
    return mapping.get(
        event_type,
        (
            "暂无明确影响",
            "AI 模型、云平台或开发工具，待观察，商业影响尚不清晰",
            "AI 应用场景，待观察，需结合后续采用情况判断",
            "行业事件 -> 生态或需求变化 -> 产业链影响有待验证",
        ),
    )


def score_item(item: Dict[str, Any]) -> int:
    content = " ".join(
        [
            text_of(item, "title", "title_en", "summary", "description"),
            text_of(item, "category"),
        ]
    ).lower()
    score = 0
    for _, keywords in EVENT_KEYWORDS:
        score += sum(1 for keyword in keywords if keyword.lower() in content)
    if link_of(item) != "暂无链接":
        score += 2
    if item_time(item):
        score += 1
    return score


def select_items(items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    seen: Set[str] = set()
    unique: List[Dict[str, Any]] = []
    for item in items:
        title = text_of(item, "title", "title_en")
        link = link_of(item)
        key = link if link != "暂无链接" else title
        if not title or key in seen:
            continue
        seen.add(key)
        unique.append(item)

    unique.sort(key=lambda item: (score_item(item), item_time(item) or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
    return unique[:limit]


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


def push_to_feishu(webhook_url: str, text: str) -> None:
    payload = {"msg_type": "text", "content": {"text": text}}
    data = http_json(webhook_url, method="POST", payload=payload)
    if isinstance(data, dict) and data.get("StatusCode") not in (None, 0):
        raise RuntimeError(f"Feishu webhook returned an error: {data}")
    if isinstance(data, dict) and data.get("code") not in (None, 0):
        raise RuntimeError(f"Feishu webhook returned an error: {data}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Push AIHOT industry briefing to Feishu.")
    parser.add_argument("--dry-run", action="store_true", help="Print the briefing instead of sending it.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of items to include.")
    parser.add_argument("--min-items", type=int, default=3, help="Fallback to 24h when recent items are below this count.")
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

        briefing = build_briefing(items, window_label=window_label)
        if args.dry_run:
            print(briefing)
            return 0

        push_to_feishu(webhook_url, briefing)
        print(f"Pushed {len(items)} AIHOT items to Feishu.")
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
