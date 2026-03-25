# Novel AI MVP

基于 `docs/novel_ai_product_tech_spec.md` 的最小可运行后端原型，覆盖三条核心链路：

1. 热门题材评分与排序。
2. 热点/爆梗候选提取与安全过滤。
3. 章节草稿生成（含章纲、亮点、记忆更新与质量门禁结果）。

## 快速启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

- `GET /health`
- `POST /api/topics/rank`
- `POST /api/hotspots/extract`
- `POST /api/chapters/generate`

接口设计对应文档中的 MVP 范围（题材榜单、热点抽取、章节生成+审核门禁）。
