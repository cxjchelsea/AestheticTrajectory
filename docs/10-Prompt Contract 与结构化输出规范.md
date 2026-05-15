# AI 审美形成系统：Prompt Contract 与结构化输出规范

## 1. 文档目的

这份文档定义系统中所有 AI prompt 的行为边界、输入格式、输出格式、失败处理和测试方式。

它的目标不是写一组最终 prompt，而是把 prompt 从“自然语言说明”变成可实现、可测试、可追踪的工程 contract。

适用范围：

- 图片底层特征提取
- 文本底层特征提取
- 动态解释候选生成
- 报告生成
- 反馈总结
- 用户画像更新
- 后续 RAG / Agent / 知识图谱扩展

## 2. 总体原则

所有 prompt 都必须遵守以下原则：

1. 输出必须结构化，优先使用 JSON。
2. 输出必须能被后端 schema 校验。
3. 不允许把解释当成事实。
4. 不允许进行人格诊断、心理疾病判断、命运化表达或玄学表达。
5. 每条高层解释必须绑定底层 evidence。
6. 不允许只输出单一结论，必须保留 alternative interpretations。
7. 必须记录 prompt version、model name、model version 和生成时间。
8. 失败时必须返回可处理的错误结构，而不是自由文本。

## 3. Prompt 文件命名规范

后续项目中建议把 prompt 放在：

```text
backend/app/ai/prompts/
```

命名格式：

```text
{module}.{purpose}.v{version}.prompt.md
```

示例：

```text
image_features.extract.v1.prompt.md
text_features.extract.v1.prompt.md
interpretations.generate.v1.prompt.md
report.generate.v1.prompt.md
profile.update.v1.prompt.md
```

每个 prompt 文件必须包含：

- Prompt ID
- Version
- System Goal
- Input Schema
- Output Schema
- Hard Constraints
- Failure Cases
- Good Examples
- Validation Rules

## 4. Prompt 管理与加载模块

MVP 阶段不需要“提示词生成模块”，需要的是“Prompt 管理与加载模块”。

它的职责是：

- 根据 `promptId` 找到 prompt 文件。
- 读取 prompt 文件内容。
- 识别 prompt version。
- 将业务输入 JSON 渲染到 prompt 中。
- 调用 LLM / 多模态模型 client。
- 解析模型输出。
- 使用 Pydantic schema 校验输出。
- 校验 evidence、uncertainty、禁止表达和安全边界。
- 记录 promptVersion、modelName、modelVersion、token usage、latency。

建议后端组件：

```text
backend/app/ai/
  prompt_registry.py
  prompt_loader.py
  prompt_renderer.py
  clients/
    llm_client.py
    vision_client.py
    embedding_client.py
  parsers/
    structured_output_parser.py
  validators/
    prompt_output_validator.py
```

调用链路：

```text
workflow step
↓
prompt_registry.get(promptId)
↓
prompt_loader.load(promptId)
↓
prompt_renderer.render(template, inputData)
↓
llm_client.generate(renderedPrompt)
↓
structured_output_parser.parse(rawOutput)
↓
prompt_output_validator.validate(parsedOutput)
↓
返回结构化结果 / 结构化错误
```

后端业务代码不应该直接拼接 prompt，也不应该直接把 LLM 原始输出保存到 PostgreSQL。

## 5. Prompt Template 与 Versioning 扩展

### 5.1 MVP 阶段

MVP 阶段只需要：

- prompt 文件固定放在 `backend/app/ai/prompts/`
- 文件名包含版本号
- `prompt_registry.py` 维护 promptId、文件名、schema、默认模型配置
- 每次调用记录 promptVersion

MVP 不需要后台页面，也不需要让模型自动生成 prompt。

### 5.2 Prompt Template 管理

后续可以把 prompt 拆成更细的 template 片段：

```text
system_message
developer_constraints
input_schema
output_schema
few_shot_examples
safety_rules
user_payload
```

适用场景：

- 同一个任务需要适配不同模型。
- 报告需要支持不同语言或不同表达风格。
- 需要复用同一套 safety rules。
- 需要对 few-shot examples 做 A/B 测试。

不建议在 MVP 阶段引入复杂 template 管理，否则会增加调试成本。

### 5.3 Prompt Versioning 管理

后续需要记录：

- promptId
- promptVersion
- promptHash
- changedAt
- changedBy
- changeReason
- compatibleOutputSchema

每条 report、insight、possible_interpretation 都应该能追溯到生成它的 promptVersion。

适用场景：

- 对比不同 prompt 版本的输出质量。
- 回溯某条洞察为何生成。
- prompt 修改后发现效果变差，需要回滚。
- 做 Evaluation 时统计不同 prompt 版本的 JSON 通过率、evidence 覆盖率和用户认可率。

MVP 可以先通过文件名和日志记录实现轻量 versioning，不需要数据库表。

## 6. 通用 Prompt Contract 模板

```text
# Prompt ID

{prompt_id}

## Version

v1

## System Goal

说明该 prompt 要完成的任务。

## Input Schema

说明输入 JSON 结构。

## Output Schema

说明输出 JSON 结构。

## Hard Constraints

说明禁止内容和必须内容。

## Failure Cases

列出错误输出示例。

## Good Examples

列出合格输出示例。

## Validation Rules

说明后端如何校验输出。
```

## 7. 图片底层特征提取 Prompt Contract

### Prompt ID

`image_features.extract.v1`

### System Goal

从图片中提取可观察、低解释度的底层视觉特征。

该 prompt 只负责观察画面，不负责判断用户性格、心理状态或审美身份。

### Input Schema

```json
{
  "inputId": "input_001",
  "imageUrl": "uploads/input_001.jpg",
  "contextText": "可选的用户说明",
  "language": "zh-CN"
}
```

### Output Schema

```json
{
  "inputId": "input_001",
  "featureType": "image",
  "lowLevelFeatures": {
    "saturation": {
      "value": "low | medium | high | unknown",
      "confidence": 0.82,
      "evidence": ["画面整体以低纯度灰蓝色为主"]
    },
    "brightness": {
      "value": "low | medium | high | unknown",
      "confidence": 0.74,
      "evidence": ["主体区域缺少高亮色块"]
    },
    "colorTemperature": {
      "value": "cool | neutral | warm | unknown",
      "confidence": 0.8,
      "evidence": ["蓝灰色占比较高"]
    },
    "colorContrast": {
      "value": "low | medium | high | unknown",
      "confidence": 0.71,
      "evidence": ["主要色块之间对比不强"]
    },
    "personPresence": {
      "value": "absent | weak | central | unknown",
      "confidence": 0.95,
      "evidence": ["画面中没有明显人物主体"]
    },
    "spatialDensity": {
      "value": "low | medium | high | unknown",
      "confidence": 0.78,
      "evidence": ["空间元素数量较少，留白明显"]
    },
    "compositionComplexity": {
      "value": "simple | medium | complex | unknown",
      "confidence": 0.7,
      "evidence": ["画面结构以少量几何块面为主"]
    },
    "textureComplexity": {
      "value": "smooth | medium | complex | unknown",
      "confidence": 0.68,
      "evidence": ["材质表面纹理变化较少"]
    },
    "moodAtmosphere": {
      "value": "calm | bright | oppressive | soft | tense | unknown",
      "confidence": 0.66,
      "evidence": ["低饱和色彩和空旷空间形成安静氛围"]
    }
  },
  "sampleEvidence": ["画面中大面积灰色墙面", "人物缺席", "空间元素较少"],
  "uncertainty": [],
  "promptVersion": "image_features.extract.v1"
}
```

### Hard Constraints

禁止：

- “用户是孤独的人”
- “用户内心压抑”
- “这说明用户灵魂干净”
- “这种审美代表高级”
- 没有 evidence 的风格结论

必须：

- 描述画面中可观察的特征。
- 如果无法确定，使用 `unknown` 或写入 `uncertainty`。
- 每个重要特征至少有一条 evidence。

### Validation Rules

- `featureType` 必须等于 `image`。
- 每个底层特征必须包含 `value`、`confidence`、`evidence`。
- `confidence` 范围必须是 0 到 1。
- 枚举字段不能输出 schema 外的值。
- 重要字段的 `evidence` 不能为空。

## 8. 文本底层特征提取 Prompt Contract

### Prompt ID

`text_features.extract.v1`

### System Goal

从用户输入文本中提取语言风格、主题、情绪倾向和表达结构。

该 prompt 只观察文本表达，不推断用户人格。

### Input Schema

```json
{
  "inputId": "input_002",
  "text": "用户输入的文字",
  "language": "zh-CN"
}
```

### Output Schema

```json
{
  "inputId": "input_002",
  "featureType": "text",
  "lowLevelFeatures": {
    "sentimentTone": {
      "value": "bright | neutral | low | unknown",
      "confidence": 0.78,
      "evidence": ["使用了“空房间”“没有回声”等表达"]
    },
    "emotionIntensity": {
      "value": "weak | medium | strong | unknown",
      "confidence": 0.7,
      "evidence": ["情绪表达克制，没有强烈情绪词"]
    },
    "narrativeDensity": {
      "value": "low | medium | high | unknown",
      "confidence": 0.76,
      "evidence": ["文本更像片段观察，而不是完整事件叙述"]
    },
    "concreteness": {
      "value": "abstract | mixed | concrete | unknown",
      "confidence": 0.72,
      "evidence": ["既有具体空间意象，也有抽象感受"]
    },
    "imageryDensity": {
      "value": "low | medium | high | unknown",
      "confidence": 0.74,
      "evidence": ["出现多个空间和光线相关意象"]
    },
    "rhythm": {
      "value": "short | calm | jumpy | expansive | unknown",
      "confidence": 0.69,
      "evidence": ["句子节奏较慢，停顿感较强"]
    },
    "timeOrientation": {
      "value": "past | present | future | circular | vague | unknown",
      "confidence": 0.63,
      "evidence": ["时间指向不明确，更像当下片段"]
    },
    "spatialReference": {
      "value": "weak | medium | strong | unknown",
      "confidence": 0.8,
      "evidence": ["反复出现房间、门、墙等空间词"]
    },
    "subjectDistance": {
      "value": "self_close | observer | de_subjective | unknown",
      "confidence": 0.67,
      "evidence": ["叙述者更像旁观者，而不是直接表达自我"]
    }
  },
  "sampleEvidence": ["原文片段 1", "原文片段 2"],
  "uncertainty": [],
  "promptVersion": "text_features.extract.v1"
}
```

### Hard Constraints

禁止：

- 根据一段文字判断用户人格。
- 将情绪信号解释成心理诊断。
- 输出“你一定是……”这类确定性表达。

必须：

- 保留原文 evidence。
- 区分 `sentimentTone`、`emotionIntensity` 等底层文本特征和高层解释。

## 9. 动态解释候选 Prompt Contract

### Prompt ID

`interpretations.generate.v1`

### System Goal

基于底层特征、相似性分组结果和用户历史，生成多个可能解释，而不是生成唯一真相。

### Input Schema

```json
{
  "jobId": "job_001",
  "userId": "user_001",
  "similarityGroups": [],
  "globalPatterns": [],
  "recentFeatures": [],
  "userHistory": [],
  "feedbackSummary": []
}
```

### Output Schema

```json
{
  "jobId": "job_001",
  "interpretations": [
    {
      "interpretationId": "interp_001",
      "name": "偏向安静空间的视觉选择",
      "summary": "近期输入中反复出现低密度构图、人物缺席和柔和色彩。",
      "evidenceRefs": [
        {
          "inputId": "input_001",
          "feature": "composition.density",
          "value": "low"
        }
      ],
      "confidence": 0.78,
      "uncertainty": "样本数量仍然较少，不能判断这是稳定偏好。",
      "alternativeInterpretations": [
        "也可能是当前收集的素材主题较集中。",
        "也可能只是某一阶段的视觉兴趣。"
      ],
      "riskFlags": []
    }
  ],
  "rejectedClaims": [
    {
      "claim": "用户性格孤独",
      "reason": "超出审美观察范围，缺少可验证 evidence。"
    }
  ],
  "promptVersion": "interpretations.generate.v1"
}
```

### Hard Constraints

禁止：

- 人格诊断。
- 心理疾病推断。
- 命运化表达。
- 作者中心化解释。
- 把某种风格描述成更高级。
- 所有样本都强行解释成同一种主题。

必须：

- 至少输出 2 条解释候选。
- 每条解释必须绑定 `evidenceRefs`。
- 每条解释必须有 `uncertainty`。
- 每条解释必须有 `alternativeInterpretations`。
- 无法解释时应降低 confidence，而不是编造原因。

### Failure Cases

错误示例：

```text
你是一个孤独的人，所以喜欢空旷画面。
```

```text
你的灵魂倾向于安静和纯净。
```

```text
这些图片说明你拥有高级审美。
```

合格示例：

```text
近期输入中反复出现人物缺席、低空间密度和低饱和色彩，因此系统观察到一种偏向安静空间的视觉选择。但由于样本数量有限，这也可能只是当前素材主题造成的阶段性现象。
```

## 10. 报告生成 Prompt Contract

### Prompt ID

`report.generate.v1`

### System Goal

将底层特征、相似性分组结果和解释候选组织成用户可读的审美报告。

报告要清晰、有依据、有温度，但不能把审美解释变成人格判断。

### Input Schema

```json
{
  "reportId": "report_001",
  "userId": "user_001",
  "analysisJobId": "job_001",
  "featureSummary": {},
  "similarityGroupSummary": {},
  "interpretations": [],
  "feedbackHistory": []
}
```

### Output Schema

```json
{
  "reportId": "report_001",
  "title": "近期审美观察报告",
  "summary": "",
  "sections": [
    {
      "sectionType": "observation | interpretation | alternative | evolution | suggestion",
      "title": "",
      "content": "",
      "evidenceRefs": []
    }
  ],
  "insights": [
    {
      "insightId": "insight_001",
      "content": "",
      "evidenceRefs": [],
      "confidence": 0.7,
      "feedbackRequired": true
    }
  ],
  "disclaimer": "这是一份基于当前输入的审美观察，不是人格诊断或心理评估。",
  "promptVersion": "report.generate.v1"
}
```

### Hard Constraints

禁止：

- 使用心理测试、星座、命运、灵魂等表达。
- 用“你就是”“你一定”描述用户。
- 把系统推测包装成事实。

必须：

- 区分观察和解释。
- 在报告中保留“不确定性”。
- 每条重要洞察可追溯到 evidence。

## 11. 用户画像更新 Prompt Contract

### Prompt ID

`profile.update.v1`

### System Goal

根据用户历史输入、报告和反馈，更新长期审美画像。

画像只记录稳定偏好、变化趋势和用户明确认可或否定的解释，不记录人格结论。

### Input Schema

```json
{
  "userId": "user_001",
  "previousProfile": {},
  "newReport": {},
  "feedback": []
}
```

### Output Schema

```json
{
  "userId": "user_001",
  "stablePreferences": [],
  "emergingPatterns": [],
  "rejectedInterpretations": [],
  "acceptedInterpretations": [],
  "profileConfidence": 0.65,
  "updateReason": "",
  "promptVersion": "profile.update.v1"
}
```

### Hard Constraints

禁止：

- 将短期输入写成长期稳定偏好。
- 将用户否定的解释继续写入画像。
- 保存心理诊断式标签。

必须：

- 区分 stable 和 emerging。
- 记录 update reason。
- 尊重用户反馈。

## 12. Prompt 输出失败处理

后端调用 LLM 后必须进行 schema 校验。

如果输出无法解析：

```json
{
  "status": "failed",
  "errorType": "INVALID_JSON",
  "retryable": true,
  "rawOutputStored": true
}
```

如果输出违反安全边界：

```json
{
  "status": "failed",
  "errorType": "POLICY_VIOLATION",
  "retryable": false,
  "violations": [
    "personality_diagnosis"
  ]
}
```

如果 evidence 缺失：

```json
{
  "status": "failed",
  "errorType": "MISSING_EVIDENCE",
  "retryable": true
}
```

## 13. Prompt 测试方式

每个 prompt 至少需要以下测试：

- Schema 测试：输出能通过 JSON schema / Pydantic schema 校验。
- 边界测试：输入极少、输入混乱、输入风格偏离开发者偏好时，输出仍不越界。
- 安全测试：不得输出人格诊断、心理推断、玄学表达。
- Evidence 测试：解释必须能追溯到底层特征或原始输入。
- 一致性测试：相同输入多次运行，核心结构不能大幅漂移。
- 去作者中心化测试：不同审美风格样本不能被统一解释成开发者偏好的主题。

## 14. 开发提示

后续让 AI 编写代码时，可以使用以下约束：

```text
请根据 `10-Prompt Contract 与结构化输出规范.md` 实现对应 prompt 调用。

要求：
1. prompt 输出必须通过 Pydantic schema 校验。
2. 不允许把 LLM 原始输出直接返回给前端。
3. 所有解释必须绑定 evidenceRefs。
4. 记录 promptVersion、modelName、modelVersion。
5. 失败时返回结构化错误，并写入 analysis_logs。
```




