# V3-B：Aesthetic Knowledge RAG

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-17
```

## 1. 本轮目标

在 V3-A history context 之上，引入最小 aesthetic knowledge RAG：

```text
用户完成分析
↓
workflow 基于当前特征检索项目内置审美知识库
↓
生成 knowledgeContext 并写入 report_json
↓
报告详情页展示“知识参考”
↓
知识 reference 只用于解释风格概念，不进入 profile positive evidence
```

## 2. 上游版本决策

引用 `docs/iterations/v3-0-personalized-retrieval-research.md`：

- RAG 只做 explanation support，不做 preference evidence。
- 外部知识不得替代 input evidence。
- 不接入 ChromaDB runtime、LangSmith、OpenTelemetry。
- 不把知识库内容写入用户画像。

## 3. 方案选择

采用：

```text
内置静态 knowledge chunks + 特征标签启发式匹配
```

原因：

- V3-B 目标是验证 knowledge context 边界，不是搭建大规模向量知识库。
- 当前 mock feature extractor 输出稳定，可用 feature key 做 deterministic 匹配。
- 与 V3-A 的纯函数 + workflow step 模式一致。

## 4. 实现摘要

- 新增 `AestheticKnowledgeContext` / `KnowledgeContextItem` schema。
- 新增 `backend/app/ai/knowledge/aesthetic_knowledge_base.py` 静态知识条目。
- 新增 `aesthetic_knowledge_retrieval` service 与 `retrieve_aesthetic_knowledge` workflow step。
- `ReportResponse.knowledgeContext` 持久化到 `report_json`。
- 前端 `ReportDetailPage` 新增“知识参考”区块。
- Developer Debug 拆分 history retrieval 与 aesthetic knowledge RAG boundary warnings。

## 5. 验收标准

- 报告详情页展示知识参考，且带来源 refs。
- 知识 reference 与 insight evidenceRefs 分离。
- 知识 reference 不进入 profile positive evidence。
- 无匹配时返回明确 message，不伪造偏好结论。

## 6. 测试记录

```text
2026-06-17：
- 后端：REPOSITORY_BACKEND=memory python -m pytest backend/app/tests -q，36 passed, 3 warnings。
- 前端：npm run build，通过。
```

## 7. 人工验收

```text
2026-06-17：
- 用户已完成人工测试，V3-B 知识参考路径测试成功。
- 报告详情页出现“知识参考”区块。
- 每条知识参考包含 title、snippet、source refs。
- “知识参考”与“历史参考”“重点洞察”分区展示。
- Developer Debug 中出现 retrieve_aesthetic_knowledge step。
```

## 8. 下一步

```text
用户已完成 V3-B 人工验收；下一步进入 V3-C Evaluation Metrics Baseline。
```
