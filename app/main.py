from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.services import (
    TopicSignal,
    extract_hot_meme_candidates,
    filter_hot_terms,
    generate_chapter_draft,
    rank_topics,
)

app = FastAPI(title="Novel AI MVP", version="0.1.0")


class TopicSignalIn(BaseModel):
    name: str
    read_score: float = Field(ge=0, le=100)
    search_score: float = Field(ge=0, le=100)
    time_score: float = Field(ge=0, le=100)
    competition: float = Field(default=0, ge=0, le=100)
    novelty: float = Field(default=0, ge=0, le=100)
    anomaly_penalty: float = Field(default=0, ge=0, le=100)


class TopicRankRequest(BaseModel):
    signals: list[TopicSignalIn]
    top_n: int = Field(default=10, ge=1, le=100)


class MemeRequest(BaseModel):
    corpus: list[str]
    baseline_frequency: dict[str, float] = Field(default_factory=dict)


class ChapterRequest(BaseModel):
    topic: str
    constraints: dict = Field(default_factory=dict)
    hot_terms: list[str] = Field(default_factory=list)
    memory: dict = Field(default_factory=dict)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/topics/rank")
def topics_rank(req: TopicRankRequest) -> dict:
    signals = [TopicSignal(**item.model_dump()) for item in req.signals]
    return {"topics": rank_topics(signals, req.top_n)}


@app.post("/api/hotspots/extract")
def hotspots_extract(req: MemeRequest) -> dict:
    candidates = extract_hot_meme_candidates(req.corpus, req.baseline_frequency)
    filter_result = filter_hot_terms([item["term"] for item in candidates])
    return {
        "candidates": candidates,
        "safe_terms": filter_result["safe_terms"],
        "blocked_terms": filter_result["blocked_terms"],
    }


@app.post("/api/chapters/generate")
def chapters_generate(req: ChapterRequest) -> dict:
    return generate_chapter_draft(req.topic, req.constraints, req.hot_terms, req.memory)
