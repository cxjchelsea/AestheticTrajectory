# V1-A：真实审美特征抽取

## 1. 本轮目标

把当前 mock feature extraction 升级为可替换的真实审美特征抽取能力。

本轮不是完整真实 V1，只解决第一步：

```text
图片 / 文本输入
↓
FeatureExtractor 抽象
↓
mock / real extractor 可切换
↓
结构化 InputFeature 输出
↓
schema validator 校验
↓
继续复用现有 mock workflow 和 API 行为
```

## 2. 当前基线

当前已归档状态：

```text
V1 skeleton / V1 baseline
```

已确认：

- 前端页面骨架可用。
- 文字输入 → mock report → 洞察反馈保存已通过手动验收。
- 图片样本当前只是占位 UI。
- 后端 `python -m pytest` 通过。
- 前端 `npm run build` 通过。
- API flow 集成测试已覆盖 health → inputs → analysis job → report → feedback。

当前限制：

- 未接入真实图片文件存储。
- 未读取图片内容做真实多模态分析。
- 未接入真实 LLM / vision model。
- 未持久记录完整 analysis logs。
- ChromaDB 仍是 mock metadata / 抽象替代。

## 3. 本轮解决什么问题

本轮解决：

```text
系统能否从真实图片 / 文本输入中抽取稳定、结构化、有 evidence 的审美特征？
```

本轮不解决：

- 真实 PostgreSQL 持久化。
- 真实 ChromaDB runtime 写入。
- 长期用户画像。
- 历史报告。
- RAG。
- Agent。
- MCP。
- Skill Library。
- 推荐系统。

## 4. 必须阅读的文档

只需要阅读以下文档：

1. `docs/04-审美表征体系文档.md`
2. `docs/05-AI分析逻辑文档.md`
3. `docs/09-AI Workflow 编排与任务执行文档.md`
4. `docs/10-Prompt Contract 与结构化输出规范.md`
5. `docs/13-验证与评估文档.md`
6. `docs/12-开发任务拆分与里程碑计划.md`

不要一次性读取 `03-16` 全量文档。

## 5. 实现范围

### 5.1 FeatureExtractor 抽象

需要定义统一抽象：

```text
FeatureExtractor
```

职责：

- 接收单个 `AestheticInputResponse`。
- 根据 input type 选择图片或文本抽取逻辑。
- 返回符合 `InputFeature` schema 的结构化结果。

要求：

- 保留当前 `MockFeatureExtractor`。
- 新增真实 extractor 时不能破坏现有 mock workflow。
- service / workflow 不直接拼 prompt。

### 5.2 文本审美特征抽取

文本输入需要输出：

- 情绪倾向。
- 抽象程度。
- 叙事密度。
- 意象类型。
- 节奏感。
- 空间感。
- 主体距离。
- evidence。
- confidence。
- promptVersion。
- modelName。

### 5.3 图片审美特征抽取

图片输入当前仍可先使用占位信息，但接口设计要为真实图片分析预留：

- 色彩倾向。
- 饱和度。
- 明度。
- 色温。
- 空间密度。
- 人物存在。
- 构图复杂度。
- 材质 / 纹理。
- 情绪氛围。
- evidence。
- confidence。
- promptVersion。
- modelName。

如果本轮暂时无法接入真实图片文件存储，必须在代码和文档里明确：

```text
图片真实分析依赖后续文件存储接入。
当前只完成 extractor 抽象和 mock / real 切换边界。
```

### 5.4 Schema Validator

模型输出必须经过校验后才能进入 workflow。

最低要求：

- 字段完整。
- `confidence` 在 0-1 之间。
- 每个 feature 至少有一个 evidence。
- `promptVersion` 存在。
- 不允许 LLM 原始字符串直接入库或传给报告生成。

## 6. 不允许 AI 自行决定的内容

本轮禁止自行扩大范围：

- 不新增长期用户画像。
- 不新增历史报告页面。
- 不新增 RAG。
- 不新增 Agent。
- 不新增 MCP。
- 不重构整个 workflow。
- 不改变现有 API 路径。
- 不删除 mock client。
- 不把 ChromaDB 当业务数据库。

## 7. 预期涉及文件

后端可能涉及：

```text
backend/app/ai/mock/mock_feature_extractor.py
backend/app/ai/validators/prompt_output_validator.py
backend/app/schemas/feature.py
backend/app/workflows/steps/extract_features.py
backend/app/tests/unit/
backend/app/tests/integration/
```

如果新增真实 extractor，建议放在：

```text
backend/app/ai/clients/
backend/app/ai/prompts/
backend/app/ai/parsers/
```

前端本轮原则上不改，除非需要展示真实 feature error / loading 状态。

## 8. 验收标准

本轮完成需要满足：

- mock workflow 仍可运行。
- `python -m pytest` 通过。
- 前端 `npm run build` 仍通过。
- 文本输入可以生成符合 `InputFeature` schema 的结构化特征。
- 图片输入的当前边界被明确记录。
- 非法模型输出能被 validator 识别。
- 每个特征至少包含 `value`、`confidence`、`evidence`。
- 报告仍然不包含人格诊断、玄学表达或无证据高级词。

## 9. 完成后需要更新

完成本轮后，需要更新：

- `docs/15-迭代执行记录.md`
- `docs/archive/v1/V1-遗留问题.md`
- `docs/archive/v1/V1-验收核对表.md`
- 如有接口或 schema 变化，更新对应设计文档。

## 10. 下一轮入口

如果本轮通过，下一轮进入：

```text
V1-B：Embedding 与相似性分组
```

如果本轮未通过，继续收口：

```text
FeatureExtractor 抽象
schema validator
真实图片文件存储边界
```
