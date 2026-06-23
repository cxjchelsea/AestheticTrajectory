# V5-B：Real Report Runtime

当前状态：

```text
accepted / manual_validation_passed
```

创建日期：

```text
2026-06-22
```

## 1. 本轮目标

在 V5-A identity baseline 之上，用 **真实 LLM structured output** 替换 mock interpretation / insight 生成路径：

```text
MockInterpretationGenerator（interpret + insights）
↓
InterpretationGenerator protocol + LLM factory（mock | ollama | openai）
↓
JSON schema 校验 + evidenceRefs 治理 + governance 测试
↓
workflow / debug 诚实标记 report LLM runtime
```

本轮完成后，用户应能：

- 配置 `REPORT_LLM_RUNTIME=ollama`（或 openai）后，报告中的 **possibleInterpretations** 与 **insights** 来自真实 LLM。
- `evidenceRefs` 仍 **只指向当前 job 的 input_id**；伪造 evidence → validator 拒绝或 job fail-fast。
- 默认 `REPORT_LLM_RUNTIME=mock` 时，pytest 与 V4 回归行为不退化。
- Debug 面板可见 report LLM runtime（mock / ollama / openai）及 model 名。

## 2. 上游版本决策

引用 `docs/iterations/v5-0-production-runtime-trust-boundary-research.md` §12、`v5-a` 已验收：

- V5-B **只替换 interpretation + insight 生成**；feature extraction、embedding、clustering 算法保持 V4 baseline。
- **不做 vision** 内容解析（V5-0：vision 可选延后，不阻塞 V5-B）。
- **不做** 无 schema 自由文本报告；必须 JSON + Pydantic validator。
- LLM 输出 **不得** 直接进入 profile positive evidence（仍须用户 feedback）。
- 未配置 real runtime 凭证时 **fail-fast**，不 silent 回退 mock（与 V4-A embedding 治理一致）。
- 不做 OAuth MCP（V5-C）、不做 Chroma/LLM 全链路 resilience 批次（V5-D）。

## 3. 本轮解决什么问题

```text
如何在保持 ReportResponse / Insight / PossibleInterpretation schema 与 evidence-first 治理不变的前提下，把 cluster_inputs 中的 mock 解释生成换成可配置的真实 LLM runtime？
```

本轮不解决：

- 真实 vision / 图片内容理解（feature 仍 mock/heuristic）。
- 真实 feature extraction LLM 路径。
- report summary 必须 100% LLM 化（首版可保留 heuristic summary，insights 必须 real 路径产出）。
- OAuth MCP、identity 变更、multi-agent。
- LangSmith / OTel pipeline（V5-D 可选）。

## 4. 当前实现快照（V5-B 起点）

| 能力 | 当前状态 |
| --- | --- |
| 相似性分组 | `cluster_inputs.py`：embedding cosine + feature overlap，**非 LLM** |
| 解释/洞察 | `MockInterpretationGenerator.interpret/insights`，硬编码在 `cluster_inputs` |
| 报告组装 | `generate_report.py`：heuristic title/summary + scoped IDs |
| Feature | `MockFeatureExtractor` / heuristic，V5-B 不改 |
| Embedding factory | `get_embedding_client()` mock/ollama/openai 已有 |
| LLM report factory | **不存在** |
| Prompt 文件 | `docs/10` 有 contract，`backend/app/ai/prompts/` **未实现** |
| Validator | `prompt_output_validator.py` 仅 InputFeature |
| Debug mockUsage | 标记 `MockInterpretationGenerator` enabled |
| 用户环境 | `.env` 有 `LLM_BASE_URL` 远程 Ollama；`EMBEDDING_RUNTIME=mock` |

## 5. 外部调研与方案选择

### 5.1 调研问题与结论摘要

| 问题 | 结论 |
| --- | --- |
| 替换范围 | **interpret + insights** 由 LLM 一次或分步 JSON 生成；clustering 保留算法 |
| Runtime 切换 | `REPORT_LLM_RUNTIME=mock\|ollama\|openai`，**无 shadow compare**（对齐 V4-A） |
| 默认 runtime | **mock**（CI / pytest 兼容） |
| ollama 无服务 | **fail-fast**，job failed，debug 明示 |
| openai 无 key | **fail-fast** |
| Prompt 形态 | 首版实现 `interpretations.generate.v1` 合并输出 interpretations + insights JSON |
| Schema 映射 | LLM JSON → `PossibleInterpretation` + `Insight`；report-scoped ID 仍由 `generate_report` 后缀 |
| evidenceRefs 治理 | 后处理 validator：`evidenceRefs ⊆ current_input_ids` |
| 治理关键词 | 拒绝/标记：人格诊断、心理评估、命运、灵魂、星座等（见 `docs/10`、`docs/13`） |
| summary/title | V5-B **保留 heuristic** `_build_summary`；LLM 可只产出 insights/interpretations |
| 历史/知识上下文 | 注入 prompt 作为 **只读 supplementary**；不得写入 evidenceRefs |
| 测试策略 | Fake LLM client 单测 + mock 默认集成回归；可选 marked real-ollama 人工测试 |

### 5.2 不采用方案

| 方案 | 原因 |
| --- | --- |
| 全链路 end-to-end 一个 LLM 调用输出整份 ReportResponse | schema 过大、难验证、难回归 |
| shadow mode 并行 mock/real compare | V5-B 范围外；增加复杂度 |
| LLM 失败 silent 回退 mock | 违反项目治理；与 embedding 策略不一致 |
| 让 LLM 自由生成 evidenceRefs（含 history/knowledge ID） | 破坏 evidence-first；V3–V4 治理回退 |
| 首版接 vision multimodal | V5-0 明确 text 优先 |

### 5.3 最终方案选择

#### 5.3.1 配置项（`.env`）

```text
REPORT_LLM_RUNTIME=mock|ollama|openai     # 默认 mock
REPORT_LLM_MODEL=llama3.2|gpt-4o-mini|... # runtime 对应模型
REPORT_LLM_TIMEOUT_SECONDS=120
OPENAI_API_KEY=                           # openai 时必填
OLLAMA_BASE_URL=                          # ollama 时必填（可复用 LLM_BASE_URL）
```

与 embedding 配置 **独立**：允许 `EMBEDDING_RUNTIME=mock` + `REPORT_LLM_RUNTIME=ollama`。

#### 5.3.2 模块与目录

```text
backend/app/ai/interpretation_generator.py       # Protocol
backend/app/ai/mock/mock_interpretation_generator.py  # 保留，实现 Protocol
backend/app/ai/ollama/ollama_interpretation_generator.py
backend/app/ai/openai/openai_interpretation_generator.py  # 可选，与 ollama 二选一起步
backend/app/ai/factory.py                        # + get_interpretation_generator()
backend/app/ai/prompts/interpretations.generate.v1.prompt.md
backend/app/ai/prompt_loader.py                  # 最小 loader
backend/app/ai/validators/report_llm_output_validator.py
backend/app/workflows/steps/generate_interpretations.py  # 从 cluster_inputs 拆出 LLM 步
```

#### 5.3.3 Workflow 变更

```text
extract_features          # 不变
generate_embeddings       # 不变
write_vectors             # 不变
cluster_inputs            # 仅返回 SimilarityGroup[]（去掉 mock interpret/insights）
generate_interpretations  # 新 step：factory → LLM/mock → validate
retrieve_personal_history # 不变
retrieve_aesthetic_knowledge
generate_report           # 不变（scoped IDs + heuristic summary）
compute_report_evaluation
save_report / update_trajectory
```

`analysis_logs` 新增 step_id：`generate_interpretations`。

#### 5.3.4 LLM 输出 JSON（实现 schema，对齐 docs/10 §9 简化版）

```json
{
  "promptVersion": "interpretations.generate.v1",
  "modelName": "llama3.2",
  "interpretations": [
    {
      "id": "interpretation_001",
      "name": "...",
      "confidence": 0.72,
      "evidenceRefs": ["input_xxx"],
      "uncertainty": "..."
    }
  ],
  "insights": [
    {
      "insightId": "insight_001",
      "title": "...",
      "observation": "...",
      "interpretation": "...",
      "evidenceRefs": ["input_xxx"],
      "uncertainty": "...",
      "confidence": 0.68
    }
  ],
  "rejectedClaims": []
}
```

约束：

- `interpretations` ≥ 1；V5-B 首版 insights ≥ 1。
- 每条 `evidenceRefs` 非空且 ⊆ 当前 job `input_ids`。
- 不得含 governance 禁用语（validator 扫描）。

#### 5.3.5 Debug / mockUsage 扩展

| runtime | mockUsage 期望 |
| --- | --- |
| mock | `MockInterpretationGenerator` enabled |
| ollama | `OllamaInterpretationGenerator` disabled(mock)；`MockInterpretationGenerator` disabled |
| openai | 同上 |

`boundaryWarnings` 中 `Real vision / LLM runtime`：real 路径下从 `not_used` → `dev_only` 或新 status（实现时定，必须在 debug 可见）。

可选：`llmTrace` 记录 model、latency、promptVersion（不含完整 prompt 正文）。

#### 5.3.6 降级边界

| 场景 | 行为 |
| --- | --- |
| `REPORT_LLM_RUNTIME=mock` | 现有 mock 逻辑，CI 默认 |
| `REPORT_LLM_RUNTIME=ollama` 且 unreachable | job **failed**，Level 0 fail-fast |
| LLM 返回非法 JSON / schema fail | job **failed**，analysis_log 记录 validator 错误 |
| LLM 返回 governance 违规文本 | job **failed** 或 strip + fail（首版 **fail-fast**） |

Chroma/knowledge 失败语义 **不在 V5-B 改**（V5-D）。

## 6. 系统边界

### 6.1 必做

- [ ] `REPORT_LLM_RUNTIME` 配置 + `get_interpretation_generator()` factory。
- [ ] `generate_interpretations` workflow step + analysis_log。
- [ ] `interpretations.generate.v1` prompt 文件 + loader。
- [ ] Ollama 真实路径（用户环境已有远程 `LLM_BASE_URL`）。
- [ ] `report_llm_output_validator`：schema + evidenceRefs + governance keywords。
- [ ] Debug mockUsage / boundaryWarnings 更新。
- [ ] `test_v5b_governance_validation.py` + 单元测试（fake LLM）。
- [ ] mock 默认全量 pytest 不退化。
- [ ] 人工验收清单 §8.3。

### 6.2 不做

- [ ] Vision / 图片内容 LLM 特征。
- [ ] Feature extraction LLM 化。
- [ ] Shadow mode mock vs real diff。
- [ ] LLM 生成 profile 写入。
- [ ] OAuth MCP / resilience 全链路。

## 7. 架构影响

### 7.1 后端

- `config.py`：report LLM 配置项。
- `cluster_inputs.py`：只产出 groups。
- `aesthetic_analysis_v1.py`：插入 `generate_interpretations` step。
- `analysis_job_service.get_debug`：mockUsage / boundary / 可选 llmTrace。

### 7.2 前端

- 无必须 UI 变更；Debug 若新增 `llmTrace` 可选展示。
- 报告页文案仍来自后端 disclaimer；不额外声称「AI 诊断」。

### 7.3 权威文档（实现前/后）

- `docs/10`：补充实现态说明（prompt 文件路径、validator 规则）。
- `docs/11`：interpretation generator 模块契约、factory env。
- `docs/13`：V5-B governance 检查项。
- `docs/23-Skill与能力沉淀设计文档.md`（拟）：V5-B 后 partial registry（workflow step → adapter）。

## 8. 验收标准

### 8.1 自动化

- pytest 全量通过（mock 默认）。
- `test_v5b_governance_validation.py` 通过。
- V4-E + V5-A 回归测试仍通过。

### 8.2 人工验证

- `REPORT_LLM_RUNTIME=ollama` + 可用 `LLM_BASE_URL`：完成分析，insights 文本非 mock 模板句式。
- Debug：`MockInterpretationGenerator` disabled；real generator 可见。
- insight `evidenceRefs` 可在 UI Evidence 中对应到当前输入。
- `REPORT_LLM_RUNTIME=mock`：与 V5-A 验收后行为一致。

### 8.3 人工验收清单

- [x] ollama 路径生成报告且 job completed。
- [x] evidenceRefs 只含当前 input id（UI 展示 inputId + 标题 + 正文，2026-06-22 修复）。
- [x] 报告/洞察无人格诊断、心理评估、命运化用语。
- [ ] LLM 不可达时 job failed（非 silent mock）— 未测，非阻塞。
- [x] mock 默认路径回归通过（pytest 109 passed）。
- [x] Debug 可见 report LLM runtime 边界（OllamaInterpretationGenerator / boundaryWarnings）。

## 9. AI 生成代码顺序（候选）

1. Config + `InterpretationGenerator` protocol + factory
2. Prompt 文件 + loader + output pydantic schemas
3. `report_llm_output_validator` + governance keyword checks
4. Refactor `cluster_inputs`；新增 `generate_interpretations`
5. Ollama generator 实现
6. Wire workflow + analysis_log step
7. Debug mockUsage / boundaryWarnings / optional llmTrace
8. Tests（unit fake LLM + governance + integration mock）
9.（可选）OpenAI generator
10. 文档 + `docs/15` §28

## 10. 权威设计文档更新判断

```text
V5-B §11 确认后、实现开始前：
- docs/10：实现态与 interpretations.generate.v1 文件路径
- docs/11：InterpretationGenerator / factory / generate_interpretations 契约
- docs/13：V5-B governance 检查项
实现完成后更新 docs/15 §28。
```

## 11. 用户确认（已接受，2026-06-22）

- [x] 接受 V5-B 范围：**仅 interpret + insights LLM 化**；feature/embedding/clustering 保持 mock/算法。
- [x] 接受 `REPORT_LLM_RUNTIME=mock|ollama|openai`，默认 mock，**无 shadow mode**。
- [x] 接受 real runtime 不可达或 validator 失败时 **job fail-fast**（不 silent 回退 mock）。
- [x] 接受首版 **Ollama 为优先 real 路径**；OpenAI 同阶段 deferred。
- [x] 接受 report **title/summary 首版仍 heuristic**；insights/interpretations 必须走 LLM（real 模式下）。
- [x] 接受 **不做 vision** 于 V5-B。
- [x] 确认后按 §9 顺序开始实现。

## 12. 当前结论

```text
V5-B 已验收通过，状态 accepted / manual_validation_passed。
验收路径：REPORT_LLM_RUNTIME=ollama，REPORT_LLM_MODEL=qwen2.5:7b-instruct，
远程 LLM_BASE_URL；insights 为真实 LLM 输出，Debug mockUsage 正确。
验收修复：OllamaInterpretationGenerator InputFeature 字段；mockUsage ollama 显示；
前端 evidenceRefs 与 server input id 对齐及展示优化。
pytest：109+ passed。
下一子阶段：V5-C Production MCP OAuth（任务单已起草，待 §11 确认）。
```
