from app.services import TopicSignal, extract_hot_meme_candidates, filter_hot_terms, rank_topics


def test_rank_topics_descending():
    signals = [
        TopicSignal(name="都市异能", read_score=90, search_score=88, time_score=75),
        TopicSignal(name="末日求生", read_score=70, search_score=68, time_score=80),
    ]

    result = rank_topics(signals, top_n=2)
    assert result[0]["hot_score"] >= result[1]["hot_score"]


def test_filter_hot_terms_blocks_risky_entries():
    result = filter_hot_terms(["职场逆袭", "地震玩梗模板", "系统流"])
    assert "地震玩梗模板" in result["blocked_terms"]
    assert "职场逆袭" in result["safe_terms"]


def test_extract_hot_meme_candidates_returns_burst_terms():
    corpus = [
        "逆天改命 爽点 爽点",
        "爽点 反转 名场面",
        "名场面 爽点",
    ]
    baseline = {"爽点": 1.0, "名场面": 0.5}

    result = extract_hot_meme_candidates(corpus, baseline)
    assert any(item["term"] == "爽点" for item in result)
