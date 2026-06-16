# V1-A：真实审美特征抽取

当前状态：

```text
accepted / archived
```

实现日期：

```text
2026-06-16
```

验收日期：

```text
2026-06-16
```

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

## 5. 调研与方案选择

流程补正说明：

```text
本节为 2026-06-16 在 V1-A 已实现并验收后补充。
补充目的不是改变实现结论，而是补齐固定开发流程中“先调研，再设计，再实现”的依据。
```

### 5.1 调研问题

本轮调研只围绕 V1-A，不扩展到完整 V1：

- 审美特征抽取应该直接写在 workflow 里，还是抽象成可替换模块？
- mock workflow 已经通过验收时，如何接入真实 extractor 而不破坏现有 API 行为？
- 文本输入在未接真实 LLM 前，能否先形成稳定的结构化特征边界？
- 图片输入在未接文件存储前，是否应该假装做真实视觉分析？
- 模型输出进入 workflow 前，最低需要哪些 schema 校验？

### 5.2 已有实现调研

当前项目中已有：

- `MockFeatureExtractor`：能生成符合旧版 `InputFeature` 的 mock 特征。
- `extract_features` workflow step：直接实例化 mock extractor。
- `InputFeature` schema：已有 `inputId`、`featureType`、`lowLevelFeatures`、`sampleEvidence`、`promptVersion`。
- `validate_structured_output`：只有基础 Pydantic schema validate，没有 feature 级业务校验。
- 前端和报告链路已经依赖现有 `lowLevelFeatures` 结构。

已有实现的主要问题：

- workflow 直接依赖 `MockFeatureExtractor`，后续无法平滑切换真实 extractor。
- `InputFeature` 缺少 `modelName`，不利于后续观测和追踪。
- evidence 非空、`promptVersion` 非空等关键约束没有独立 validator。
- 图片输入当前没有真实文件内容，不能做真实视觉分析。

### 5.3 外部参考与可借鉴模式

本轮没有做大范围外部产品调研，只采用通用工程模式：

- 抽象接口 / 协议：用统一 `FeatureExtractor` 隔离 mock、启发式和未来真实模型实现。
- 结构化输出校验：模型输出必须先转成 schema 对象，再进入 workflow。
- prompt / model 可追踪：每个模型生成结果保留 `promptVersion` 和 `modelName`。
- 渐进替换：先保留 mock workflow，再新增可替换边界，避免一次性切换真实模型。

不能照搬：

- 不能在没有图片文件存储时声称已经完成真实图片分析。
- 不能让 LLM 原始字符串直接进入报告生成或存储。
- 不能因为接入真实 extractor 就改变现有 API 路径。
- 不能在 V1-A 提前实现长期画像、RAG、Agent 或推荐。

### 5.4 可选方案

方案 A：直接接入真实 LLM / vision model。

- 优点：更接近真实 V1。
- 问题：当前没有图片文件存储、模型配置、失败处理和成本观测，会一次性扩大范围。
- 结论：本轮不采用。

方案 B：先建立 `FeatureExtractor` 抽象，保留 mock，新增本地启发式文本 extractor，图片明确 placeholder。

- 优点：能完成抽象边界和 schema 校验，且不破坏现有 workflow。
- 问题：文本效果不是最终真实模型效果，图片仍不能真实分析。
- 结论：本轮采用。

方案 C：继续只使用 mock，不新增抽象。

- 优点：改动最小。
- 问题：无法支撑后续真实模型替换，也无法验证 validator 边界。
- 结论：不采用。

### 5.5 本轮最终采用方案

最终采用：

```text
FeatureExtractor 抽象
MockFeatureExtractor 默认保留
HeuristicFeatureExtractor 作为本地文本抽取边界
图片输入返回明确 placeholder feature
InputFeature 新增 modelName
validate_input_feature 负责业务校验
workflow 支持 extractor 注入
```

采用原因：

- 符合 V1-A 的核心目标：建立真实特征抽取的可替换边界。
- 不破坏 V1 skeleton 已验收的 mock workflow 和 API 行为。
- 能为后续 LLM / vision extractor 留出位置。
- 能明确记录当前图片真实分析的前置依赖：文件存储接入。

## 6. 系统边界

本轮包含的能力：

- `FeatureExtractor` 抽象。
- mock / heuristic extractor 切换边界。
- `InputFeature` schema 增补 `modelName`。
- feature 输出业务校验。
- workflow 注入 extractor。

本轮暂缓的能力：

- 真实 LLM / vision model runtime。
- 真实图片文件存储。
- 图片内容读取和多模态分析。
- analysis log 持久化。

本轮明确不做：

- PostgreSQL runtime 持久化。
- ChromaDB runtime 写入。
- 历史报告。
- 长期用户画像。
- RAG。
- Agent。
- MCP。
- Skill Library。
- 推荐系统。

边界原因：

```text
V1-A 只负责把“特征抽取”从 mock workflow 中抽象出来，并建立后续真实模型接入的工程边界。
真实图片分析依赖文件存储和图片读取，不能在当前前置条件缺失时伪装完成。
```

## 7. 架构设计

本轮涉及的前端：

- 不涉及页面改造。
- 只同步 `InputFeature.modelName` TypeScript 类型和前端 mock data。

本轮涉及的后端：

- `FeatureExtractor` 抽象。
- `MockFeatureExtractor` 默认实现。
- `HeuristicFeatureExtractor` 本地文本实现。
- `validate_input_feature` 业务校验。
- `extract_features` workflow step 支持注入 extractor。

本轮涉及的数据库：

- 不涉及数据库表或 repository 持久化改造。
- `InputFeature` schema 有字段变化，但仍保存在现有 in-memory store。

本轮涉及的 Agent Runtime：

- 不涉及。
- 本轮不引入 Agent、自主规划或工具调用。

本轮涉及的工具层：

- 不涉及外部工具。
- 仅使用本地 Python 代码和 Pydantic schema 校验。

本轮涉及的记忆层：

- 不涉及长期记忆或用户画像。
- 只产生当前 report workflow 所需的 input feature。

本轮调用关系：

```text
run_mock_aesthetic_analysis
↓
extract_features(inputs, extractor=None)
↓
MockFeatureExtractor / HeuristicFeatureExtractor
↓
InputFeature
↓
validate_input_feature
↓
store.features
```

## 8. 模块契约

### 8.1 FeatureExtractor

模块职责：

- 接收单个 `AestheticInputResponse`。
- 返回符合 `InputFeature` schema 的结构化特征。

上游模块：

- `extract_features` workflow step。

下游模块：

- `validate_input_feature`。
- report generation workflow。

输入：

- `AestheticInputResponse`
- `index`

输出：

- `InputFeature`

异常情况：

- 输出缺少 required field。
- feature confidence 越界。
- feature evidence 为空。

权限边界：

- 只能处理用户已提交的 input record。
- 不能读取本地任意文件。

验收标准：

- mock workflow 仍可运行。
- 可注入其他 extractor 实现。

### 8.2 HeuristicFeatureExtractor

模块职责：

- 在未接真实 LLM 前，提供本地文本特征抽取边界。
- 对图片输入返回明确 placeholder，不伪装真实图片分析。

输入：

- 文本 input 的 `contentText`、`description`、`title`。
- 图片 input 的 `title` 或 placeholder 信息。

输出：

- 文本：`sentimentTone`、`narrativeDensity`、`imageryType`、`subjectDistance` 等结构化 feature。
- 图片：`imageStorageStatus`、`saturation=unknown` 等 placeholder feature。

不涉及：

- 不调用真实 LLM。
- 不读取图片二进制。
- 不做视觉模型推理。

### 8.3 validate_input_feature

模块职责：

- 在 feature 进入 workflow 后续步骤前做业务级校验。

校验内容：

- `promptVersion` 非空。
- `modelName` 非空。
- `lowLevelFeatures` 非空。
- `sampleEvidence` 非空。
- 每个 feature signal 的 evidence 非空。

不涉及：

- 不修复模型输出。
- 不做 LLM retry。
- 不保存日志。

## 9. 数据模型

核心实体：

- `InputFeature`
- `FeatureSignal`

字段设计：

- `FeatureSignal.value`
- `FeatureSignal.confidence`
- `FeatureSignal.evidence`
- `InputFeature.inputId`
- `InputFeature.featureType`
- `InputFeature.lowLevelFeatures`
- `InputFeature.sampleEvidence`
- `InputFeature.promptVersion`
- `InputFeature.modelName`

实体关系：

- 一个 `AestheticInputResponse` 对应一个 `InputFeature`。
- 一个 `InputFeature` 包含多个 `FeatureSignal`。

状态流：

```text
input created
↓
feature extracted
↓
feature validated
↓
feature stored in current repository
↓
report generation
```

索引 / 查询需求：

- 本轮不涉及真实数据库索引。

数据生命周期：

- 本轮仍沿用 in-memory store。
- 不做长期持久化和用户画像写入。

## 10. 接口设计

本轮不新增 API，也不改变现有 API 路径。

不涉及的接口改动：

- 不新增 `/api/features`。
- 不修改 `/api/inputs`。
- 不修改 `/api/analysis-jobs`。
- 不修改 `/api/reports/{report_id}`。
- 不修改 `/api/insights/{insight_id}/feedback`。

需要同步的响应结构：

- 报告中的 `lowLevelFeatures` 仍是 `InputFeature[]`。
- `InputFeature` 新增 `modelName` 字段。
- 前端 TypeScript type 已同步。

## 11. Prompt / Skill / Workflow 设计

本轮哪些地方使用 LLM：

- 不涉及真实 LLM runtime。

Prompt 输入：

- 不涉及真实 prompt 调用。
- 设计文档中保留 `text_features.extract.v1` 和 `image_features.extract.v1` contract。

Prompt 输出 schema：

- 以 `InputFeature` 为准。
- 必须包含 `promptVersion`、`modelName` 和 feature evidence。

失败处理：

- 本轮只做 schema / business validator。
- 不做 LLM retry。
- 不做自动修复。

是否沉淀为 Skill：

- 否。
- V1-A 只是模块抽象和 workflow 边界，不沉淀 Skill。

Workflow 设计：

```text
extract_features
↓
active_extractor.extract
↓
validate_input_feature
↓
return list[InputFeature]
```

## 12. AI 生成代码计划

实际执行顺序：

1. 增补 `InputFeature` schema。
2. 新增 `FeatureExtractor` 抽象。
3. 更新 `MockFeatureExtractor`，补 `modelName`。
4. 新增 `HeuristicFeatureExtractor`。
5. 新增 `validate_input_feature`。
6. 修改 `extract_features` 支持 extractor 注入。
7. 同步前端 TypeScript type 和 mock data。
8. 补充后端测试。
9. 更新 iteration、执行记录和契约文档。

每次生成的输入材料：

- V1-A iteration 文档。
- `InputFeature` schema。
- 当前 mock workflow 代码。
- Prompt Contract 中的 feature 输出规范。

每次生成后的人工检查点：

- mock workflow 是否仍通过。
- API flow 是否仍通过。
- 图片是否明确 placeholder。
- 文档是否记录未完成项。

禁止 AI 自行决定的内容：

- 不改变 API 路径。
- 不删除 mock client。
- 不伪装真实图片分析。
- 不提前引入 V2/V3/V4 能力。

## 13. 审查与测试

代码审查重点：

- 抽象是否只解决 extractor 替换问题。
- workflow 是否仍默认使用 mock。
- validator 是否阻止无 evidence 输出。
- 图片 placeholder 是否表达清楚。

单元测试：

- `InputFeature` schema 接受 `modelName`。
- `validate_input_feature` 能识别空 evidence。
- workflow 可注入 `HeuristicFeatureExtractor`。

接口测试：

- API flow 集成测试覆盖 health → inputs → analysis job → report → feedback。

端到端测试：

- 用户已完成文字链路和图片 placeholder 手动验收。

异常测试：

- 非法 feature evidence 可被 validator 识别。

LLM 输出稳定性测试：

- 不涉及。
- 本轮未接真实 LLM runtime。

安全测试：

- 不涉及新增权限。
- 图片真实文件读取未接入，因此不存在本轮文件读取权限扩大。

## 14. 重构

需要统一的命名：

- `promptVersion`
- `modelName`
- `lowLevelFeatures`
- `sampleEvidence`

需要抽象的公共能力：

- `FeatureExtractor`

需要删除的重复逻辑：

- 本轮未删除旧逻辑。
- mock 仍作为默认路径保留。

需要补充的类型定义：

- 后端 `InputFeature.model_name`
- 前端 `InputFeature.modelName`

需要补充的测试：

- 已补 feature schema / validator / extractor 注入测试。

## 15. 文档沉淀

本轮系统设计说明：

- 本文档。
- `docs/10-Prompt Contract 与结构化输出规范.md`

本轮模块说明：

- `FeatureExtractor`、`HeuristicFeatureExtractor`、`validate_input_feature` 已在本文档补充契约。

本轮接口文档：

- 不涉及新增接口。

本轮 Prompt / Skill 文档：

- Prompt Contract 已补 `modelName`。
- 不沉淀 Skill。

本轮运行说明：

- 后端：`python -m pytest`
- 前端：`npm run build`

本轮测试记录：

- 见本文档“验证记录”与 `docs/15-迭代执行记录.md`。

## 16. 复盘与下一轮计划

本轮完成了什么：

- 完成特征抽取抽象、schema validator、mock / heuristic 边界。

本轮没有完成什么：

- 真实 LLM / vision runtime。
- 真实图片文件存储。
- 图片内容读取。

最主要的失败案例：

- 流程层面：最初实现时没有先在文档中补齐调研和方案选择。

原因分析：

- 过早进入工程实现，把固定流程中的“调研 → 方案选择”压缩掉了。

下一轮需要修正什么：

- V1-B 实现前必须先完成调研与方案选择，不直接进入代码。

下一轮版本目标：

- V1-B：Embedding 与相似性分组。

是否产生可复用模块：

- 是，`FeatureExtractor` 可复用。

是否产生可复用 Skill：

- 否，本轮不沉淀 Skill。

## 17. 实现范围

### 17.1 FeatureExtractor 抽象

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

### 17.2 文本审美特征抽取

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

### 17.3 图片审美特征抽取

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

### 17.4 Schema Validator

模型输出必须经过校验后才能进入 workflow。

最低要求：

- 字段完整。
- `confidence` 在 0-1 之间。
- 每个 feature 至少有一个 evidence。
- `promptVersion` 存在。
- 不允许 LLM 原始字符串直接入库或传给报告生成。

## 18. 不允许 AI 自行决定的内容

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

## 19. 预期涉及文件

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

## 20. 验收标准

本轮完成需要满足：

- mock workflow 仍可运行。
- `python -m pytest` 通过。
- 前端 `npm run build` 仍通过。
- 文本输入可以生成符合 `InputFeature` schema 的结构化特征。
- 图片输入的当前边界被明确记录。
- 非法模型输出能被 validator 识别。
- 每个特征至少包含 `value`、`confidence`、`evidence`。
- 报告仍然不包含人格诊断、玄学表达或无证据高级词。

## 21. 完成后需要更新

完成本轮后，需要更新：

- `docs/15-迭代执行记录.md`
- `docs/archive/v1/V1-遗留问题.md`
- `docs/archive/v1/V1-验收核对表.md`
- 如有接口或 schema 变化，更新对应设计文档。

当前完成记录：

```text
已完成：
- FeatureExtractor 抽象。
- MockFeatureExtractor 默认保留。
- HeuristicFeatureExtractor 文本抽取边界。
- 图片 placeholder feature 边界。
- InputFeature schema 新增 modelName。
- validate_input_feature 校验 promptVersion、modelName、feature evidence。
- workflow 可注入 extractor。
- 前端 InputFeature 类型和 mock data 已同步 modelName。

未完成：
- 真实图片文件存储。
- 真实图片内容读取。
- 真实 LLM / vision model runtime。
```

验证记录：

```text
2026-06-16：
- backend：python -m pytest，5 passed, 3 warnings。
- frontend：npm run build，通过。

2026-06-16 手动验收：
- 用户已完成 V1-A 手动验收。
- 文字链路仍可完成上传、分析、报告展示和反馈提交。
- 图片链路边界已确认：当前仍是占位，不做真实图片内容分析。
```

验收结论：

```text
V1-A 通过验收。

已确认：
- mock workflow 仍可运行。
- FeatureExtractor 抽象和注入边界可用。
- 文本输入可以生成符合 InputFeature schema 的结构化特征。
- 图片输入真实分析边界已明确：依赖后续文件存储接入。
- 非法 feature 输出可被 validator 识别。
- 每个 feature 至少包含 value、confidence、evidence。

保留风险：
- 当前文本抽取是本地启发式实现，不是 LLM runtime。
- 图片真实内容读取尚未接入。
- Pydantic / FastAPI alias warning 后续单独收口。
```

## 22. 下一轮入口

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
