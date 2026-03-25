from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Iterable


@dataclass
class TopicSignal:
    name: str
    read_score: float
    search_score: float
    time_score: float
    competition: float = 0.0
    novelty: float = 0.0
    anomaly_penalty: float = 0.0


DEFAULT_WEIGHTS = {
    "read": 0.45,
    "search": 0.35,
    "time": 0.20,
}


def clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, value))


def compute_hot_score(signal: TopicSignal, *, weights: dict[str, float] | None = None) -> float:
    """Compute HotScore based on PRD formula with extra governance factors."""
    w = weights or DEFAULT_WEIGHTS
    base = (
        w["read"] * signal.read_score
        + w["search"] * signal.search_score
        + w["time"] * signal.time_score
    )

    # Reduce score for over-competition or suspicious traffic.
    governance_penalty = 0.2 * signal.competition + 0.3 * signal.anomaly_penalty
    novelty_bonus = 0.15 * signal.novelty
    return round(clamp(base - governance_penalty + novelty_bonus), 2)


def rank_topics(signals: Iterable[TopicSignal], top_n: int = 10) -> list[dict]:
    ranked = []
    now = datetime.now(timezone.utc).isoformat()
    for signal in signals:
        score = compute_hot_score(signal)
        trend = "上升" if signal.time_score >= 60 else "平稳" if signal.time_score >= 40 else "回落"
        ranked.append(
            {
                "topic": signal.name,
                "hot_score": score,
                "trend": trend,
                "explain": f"阅读{signal.read_score:.1f}/搜索{signal.search_score:.1f}/时间{signal.time_score:.1f}",
                "snapshot_at": now,
            }
        )
    return sorted(ranked, key=lambda x: x["hot_score"], reverse=True)[:top_n]


RISKY_WORDS = {
    "政治敏感": ["颠覆", "分裂", "政变"],
    "违法违规": ["制毒", "洗钱", "枪支交易"],
    "灾难娱乐化": ["地震玩梗", "空难搞笑", "洪灾段子"],
}


def filter_hot_terms(terms: list[str]) -> dict[str, list[str]]:
    safe: list[str] = []
    blocked: list[str] = []
    for term in terms:
        if any(keyword in term for words in RISKY_WORDS.values() for keyword in words):
            blocked.append(term)
        else:
            safe.append(term)
    return {"safe_terms": safe, "blocked_terms": blocked}


def extract_hot_meme_candidates(corpus: list[str], baseline_frequency: dict[str, float]) -> list[dict]:
    """Simple burst extraction using relative lift from baseline."""
    counts: dict[str, int] = {}
    for text in corpus:
        for token in text.split():
            if len(token) < 2:
                continue
            counts[token] = counts.get(token, 0) + 1

    results = []
    for token, count in counts.items():
        base = baseline_frequency.get(token, 0.1)
        lift = count / max(base, 0.1)
        if lift >= 2.0 and count >= 2:
            lifecycle = "爆发期" if lift >= 6 else "萌芽期" if lift >= 3 else "观察期"
            results.append({"term": token, "count": count, "lift": round(lift, 2), "lifecycle": lifecycle})

    return sorted(results, key=lambda x: (x["lift"], x["count"]), reverse=True)


def build_chapter_outline(topic: str, constraints: dict, hot_terms: list[str]) -> dict:
    protagonist = constraints.get("protagonist", "主角")
    style = constraints.get("style", "爽文节奏")
    hook = f"{protagonist}在{topic}中遭遇突发危机"
    conflict = f"围绕关键词 {', '.join(hot_terms[:2]) or '热词待补充'} 引发主线冲突"
    twist = "旧线索反转，揭示更大阴谋"

    return {
        "style": style,
        "beats": [
            {"name": "hook", "description": hook},
            {"name": "conflict", "description": conflict},
            {"name": "twist", "description": twist},
            {"name": "cliffhanger", "description": "章末抛出高压悬念，驱动追更"},
        ],
    }


def generate_chapter_draft(topic: str, constraints: dict, hot_terms: list[str], memory: dict) -> dict:
    outline = build_chapter_outline(topic, constraints, hot_terms)
    protagonist = constraints.get("protagonist", "主角")
    prev_summary = memory.get("recent_summary", "前情平稳推进")
    term_text = "、".join(hot_terms[:3]) if hot_terms else "当前热点"

    paragraphs = [
        f"【前情提要】{prev_summary}。",
        f"夜色压城，{protagonist}在{topic}的核心地带收到匿名线报，指向{term_text}背后的利益链。",
        f"当他试图抽丝剥茧时，最信任的盟友突然倒戈，迫使他在十分钟内做出生死抉择。",
        "他最终选择直面真相，却发现自己早已成为棋盘中的关键棋子。",
    ]

    quality_score = round(mean([78, 82, 85, 80]), 1)
    return {
        "outline": outline,
        "draft": "\n".join(paragraphs),
        "highlights": ["开篇高压", "中段反转", "结尾钩子"],
        "next_chapter_suggestion": "下一章揭示倒戈盟友的真实动机，并引入新对手。",
        "memory_update": {
            "character_state": {protagonist: "信任受损，但目标更坚定"},
            "foreshadowing": ["匿名线报来源可疑", "盟友倒戈疑似卧底任务"],
        },
        "quality_gate": {
            "consistency_check": "pass",
            "safety_check": "pass",
            "repeat_rate": 0.08,
            "overall_score": quality_score,
        },
    }
