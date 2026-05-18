INSERT INTO users (id, anonymous_id, created_at, updated_at)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'anonymous_mock_user_v1',
  '2026-05-15T09:00:00Z',
  '2026-05-15T09:00:00Z'
)
ON CONFLICT (id) DO UPDATE
SET anonymous_id = EXCLUDED.anonymous_id,
    updated_at = EXCLUDED.updated_at;

INSERT INTO aesthetic_inputs (id, user_id, type, content_text, file_url, source, title, description, created_at, updated_at)
VALUES
  (
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'image',
    NULL,
    '/mock/images/quiet-room.jpg',
    'mock_seed',
    '灰蓝色室内图',
    '低饱和、人物缺席、空间留白明显。',
    '2026-05-15T09:01:00Z',
    '2026-05-15T09:01:00Z'
  ),
  (
    '10000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'text',
    '房间里只剩下下午的光，回声很轻，像某种被放慢的秩序。',
    NULL,
    'mock_seed',
    '空房间片段',
    '文本偏向低密度观察，而不是完整叙事。',
    '2026-05-15T09:02:00Z',
    '2026-05-15T09:02:00Z'
  ),
  (
    '10000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    'image',
    NULL,
    '/mock/images/still-life.jpg',
    'mock_seed',
    '静物构图',
    '少量物体、柔和明暗、中心偏移。',
    '2026-05-15T09:03:00Z',
    '2026-05-15T09:03:00Z'
  ),
  (
    '10000000-0000-0000-0000-000000000004',
    '00000000-0000-0000-0000-000000000001',
    'text',
    '一段很短的路，树影停在墙上，没有人经过，也没有明确的结尾。',
    NULL,
    'mock_seed',
    '树影片段',
    '弱情节、强氛围，含留白和静止感。',
    '2026-05-15T09:04:00Z',
    '2026-05-15T09:04:00Z'
  ),
  (
    '10000000-0000-0000-0000-000000000005',
    '00000000-0000-0000-0000-000000000001',
    'image',
    NULL,
    '/mock/images/warm-object.jpg',
    'mock_seed',
    '暖色物件',
    '比其他样本更温暖，但仍保留低密度构图。',
    '2026-05-15T09:05:00Z',
    '2026-05-15T09:05:00Z'
  )
ON CONFLICT (id) DO UPDATE
SET type = EXCLUDED.type,
    content_text = EXCLUDED.content_text,
    file_url = EXCLUDED.file_url,
    source = EXCLUDED.source,
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    updated_at = EXCLUDED.updated_at;

INSERT INTO input_features (id, input_id, feature_type, model_name, prompt_version, feature_json, summary, created_at)
VALUES
  (
    '20000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    'image',
    'mock-vision-v1',
    'image_features.extract.v1',
    '{
      "inputId": "10000000-0000-0000-0000-000000000001",
      "featureType": "image",
      "lowLevelFeatures": {
        "saturation": {"value": "low", "confidence": 0.82, "evidence": ["画面整体以低饱和灰蓝色为主"]},
        "brightness": {"value": "medium", "confidence": 0.76, "evidence": ["画面没有大面积高亮区域"]},
        "spatialDensity": {"value": "low", "confidence": 0.79, "evidence": ["空间元素较少，留白面积明显"]},
        "humanPresence": {"value": "absent", "confidence": 0.88, "evidence": ["画面中没有人物主体"]}
      },
      "sampleEvidence": ["灰蓝色墙面", "空置室内空间"]
    }'::jsonb,
    '低饱和、低空间密度、人物缺席。',
    '2026-05-15T09:06:00Z'
  ),
  (
    '20000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000002',
    'text',
    'mock-llm-v1',
    'text_features.extract.v1',
    '{
      "inputId": "10000000-0000-0000-0000-000000000002",
      "featureType": "text",
      "lowLevelFeatures": {
        "sentimentTone": {"value": "low", "confidence": 0.78, "evidence": ["文本出现空房间、回声等低沉意象"]},
        "narrativeDensity": {"value": "low", "confidence": 0.72, "evidence": ["文本更像片段观察，而不是完整事件"]},
        "temporalPace": {"value": "slow", "confidence": 0.74, "evidence": ["出现被放慢的秩序"]}
      },
      "sampleEvidence": ["房间里只剩下下午的光"]
    }'::jsonb,
    '低情绪强度、低叙事密度、节奏缓慢。',
    '2026-05-15T09:07:00Z'
  ),
  (
    '20000000-0000-0000-0000-000000000003',
    '10000000-0000-0000-0000-000000000003',
    'image',
    'mock-vision-v1',
    'image_features.extract.v1',
    '{
      "inputId": "10000000-0000-0000-0000-000000000003",
      "featureType": "image",
      "lowLevelFeatures": {
        "saturation": {"value": "medium-low", "confidence": 0.75, "evidence": ["主体颜色不强烈，背景偏柔和"]},
        "compositionBalance": {"value": "asymmetric", "confidence": 0.7, "evidence": ["主体略偏离中心"]},
        "spatialDensity": {"value": "low", "confidence": 0.81, "evidence": ["画面只包含少量物体"]}
      },
      "sampleEvidence": ["少量静物", "中心偏移构图"]
    }'::jsonb,
    '低密度静物与非对称构图。',
    '2026-05-15T09:08:00Z'
  ),
  (
    '20000000-0000-0000-0000-000000000004',
    '10000000-0000-0000-0000-000000000004',
    'text',
    'mock-llm-v1',
    'text_features.extract.v1',
    '{
      "inputId": "10000000-0000-0000-0000-000000000004",
      "featureType": "text",
      "lowLevelFeatures": {
        "narrativeDensity": {"value": "low", "confidence": 0.77, "evidence": ["没有明确事件推进或结尾"]},
        "humanPresence": {"value": "absent", "confidence": 0.82, "evidence": ["文本明确写到没有人经过"]},
        "atmosphere": {"value": "quiet", "confidence": 0.8, "evidence": ["树影停在墙上的静止描写"]}
      },
      "sampleEvidence": ["树影停在墙上", "没有人经过"]
    }'::jsonb,
    '弱情节、人物缺席、静止氛围。',
    '2026-05-15T09:09:00Z'
  ),
  (
    '20000000-0000-0000-0000-000000000005',
    '10000000-0000-0000-0000-000000000005',
    'image',
    'mock-vision-v1',
    'image_features.extract.v1',
    '{
      "inputId": "10000000-0000-0000-0000-000000000005",
      "featureType": "image",
      "lowLevelFeatures": {
        "saturation": {"value": "medium", "confidence": 0.69, "evidence": ["局部暖色物件比其他样本更明显"]},
        "spatialDensity": {"value": "low", "confidence": 0.73, "evidence": ["背景和主体数量仍然克制"]},
        "temperature": {"value": "warm", "confidence": 0.71, "evidence": ["主体呈暖色调"]}
      },
      "sampleEvidence": ["暖色物件", "低密度背景"]
    }'::jsonb,
    '较暖的局部色彩，但构图仍保持低密度。',
    '2026-05-15T09:10:00Z'
  )
ON CONFLICT (id) DO UPDATE
SET feature_type = EXCLUDED.feature_type,
    model_name = EXCLUDED.model_name,
    prompt_version = EXCLUDED.prompt_version,
    feature_json = EXCLUDED.feature_json,
    summary = EXCLUDED.summary;

INSERT INTO embedding_records (id, owner_type, owner_id, collection_name, chroma_id, model_name, vector_dimension, created_at)
VALUES
  ('30000000-0000-0000-0000-000000000001', 'input', '10000000-0000-0000-0000-000000000001', 'inputs', 'chroma_mock_input_001', 'mock-embedding-v1', 8, '2026-05-15T09:11:00Z'),
  ('30000000-0000-0000-0000-000000000002', 'input', '10000000-0000-0000-0000-000000000002', 'inputs', 'chroma_mock_input_002', 'mock-embedding-v1', 8, '2026-05-15T09:11:10Z'),
  ('30000000-0000-0000-0000-000000000003', 'input', '10000000-0000-0000-0000-000000000003', 'inputs', 'chroma_mock_input_003', 'mock-embedding-v1', 8, '2026-05-15T09:11:20Z'),
  ('30000000-0000-0000-0000-000000000004', 'input', '10000000-0000-0000-0000-000000000004', 'inputs', 'chroma_mock_input_004', 'mock-embedding-v1', 8, '2026-05-15T09:11:30Z'),
  ('30000000-0000-0000-0000-000000000005', 'input', '10000000-0000-0000-0000-000000000005', 'inputs', 'chroma_mock_input_005', 'mock-embedding-v1', 8, '2026-05-15T09:11:40Z')
ON CONFLICT (id) DO UPDATE
SET chroma_id = EXCLUDED.chroma_id,
    model_name = EXCLUDED.model_name,
    vector_dimension = EXCLUDED.vector_dimension;

INSERT INTO analysis_jobs (id, user_id, status, input_count, error_message, started_at, finished_at, created_at)
VALUES (
  '40000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  'completed',
  5,
  NULL,
  '2026-05-15T09:12:00Z',
  '2026-05-15T09:14:30Z',
  '2026-05-15T09:12:00Z'
)
ON CONFLICT (id) DO UPDATE
SET status = EXCLUDED.status,
    input_count = EXCLUDED.input_count,
    error_message = EXCLUDED.error_message,
    started_at = EXCLUDED.started_at,
    finished_at = EXCLUDED.finished_at;

INSERT INTO aesthetic_reports (
  id,
  user_id,
  job_id,
  title,
  summary,
  low_level_features_json,
  similarity_groups_json,
  interpretations_json,
  report_json,
  markdown,
  created_at
)
VALUES (
  '50000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  '40000000-0000-0000-0000-000000000001',
  '近期审美观察报告',
  '这组输入呈现出低饱和、低密度、人物存在感较弱的共同倾向。',
  '[
    {"inputId": "10000000-0000-0000-0000-000000000001", "summary": "低饱和、低空间密度、人物缺席"},
    {"inputId": "10000000-0000-0000-0000-000000000002", "summary": "低情绪强度、低叙事密度、节奏缓慢"},
    {"inputId": "10000000-0000-0000-0000-000000000003", "summary": "低密度静物与非对称构图"},
    {"inputId": "10000000-0000-0000-0000-000000000004", "summary": "弱情节、人物缺席、静止氛围"},
    {"inputId": "10000000-0000-0000-0000-000000000005", "summary": "较暖色彩与低密度构图"}
  ]'::jsonb,
  '[
    {
      "groupId": "similarity_group_001",
      "name": "安静低密度组",
      "inputIds": [
        "10000000-0000-0000-0000-000000000001",
        "10000000-0000-0000-0000-000000000002",
        "10000000-0000-0000-0000-000000000004"
      ],
      "commonFeatures": ["low_saturation", "low_spatial_density", "person_absent", "quiet_atmosphere"],
      "uncertainty": "样本数量较少，该分组只表示本次输入中的相似结构。"
    },
    {
      "groupId": "similarity_group_002",
      "name": "克制静物组",
      "inputIds": [
        "10000000-0000-0000-0000-000000000003",
        "10000000-0000-0000-0000-000000000005"
      ],
      "commonFeatures": ["low_density", "object_focus", "controlled_composition"],
      "uncertainty": "该分组只说明两张图片在构图密度上接近。"
    }
  ]'::jsonb,
  '[
    {
      "interpretationId": "60000000-0000-0000-0000-000000000001",
      "name": "克制空间感",
      "confidence": 0.72,
      "evidenceRefs": [
        "10000000-0000-0000-0000-000000000001",
        "10000000-0000-0000-0000-000000000002",
        "10000000-0000-0000-0000-000000000004"
      ]
    },
    {
      "interpretationId": "60000000-0000-0000-0000-000000000002",
      "name": "弱叙事强氛围",
      "confidence": 0.67,
      "evidenceRefs": [
        "10000000-0000-0000-0000-000000000002",
        "10000000-0000-0000-0000-000000000004"
      ]
    }
  ]'::jsonb,
  '{
    "reportId": "50000000-0000-0000-0000-000000000001",
    "title": "近期审美观察报告",
    "summary": "这组输入呈现出低饱和、低密度、人物存在感较弱的共同倾向。",
    "similarityGroups": [
      {
        "groupId": "similarity_group_001",
        "name": "安静低密度组",
        "inputIds": [
          "10000000-0000-0000-0000-000000000001",
          "10000000-0000-0000-0000-000000000002",
          "10000000-0000-0000-0000-000000000004"
        ],
        "commonFeatures": ["low_saturation", "low_spatial_density", "person_absent", "quiet_atmosphere"]
      },
      {
        "groupId": "similarity_group_002",
        "name": "克制静物组",
        "inputIds": [
          "10000000-0000-0000-0000-000000000003",
          "10000000-0000-0000-0000-000000000005"
        ],
        "commonFeatures": ["low_density", "object_focus", "controlled_composition"]
      }
    ],
    "possibleInterpretations": [
      {"name": "克制空间感", "confidence": 0.72},
      {"name": "弱叙事强氛围", "confidence": 0.67}
    ],
    "insights": [
      {"insightId": "70000000-0000-0000-0000-000000000001", "title": "你近期可能更容易被安静、低密度的结构吸引"},
      {"insightId": "70000000-0000-0000-0000-000000000002", "title": "样本中有一种弱叙事、强氛围的倾向"},
      {"insightId": "70000000-0000-0000-0000-000000000003", "title": "暖色样本更像局部变化，而不是整体偏好翻转"}
    ],
    "disclaimer": "这是一份基于当前输入的审美观察，不是人格诊断、心理评估或长期画像。"
  }'::jsonb,
  '# 近期审美观察报告\n\n这组输入呈现出低饱和、低密度、人物存在感较弱的共同倾向。',
  '2026-05-15T09:15:00Z'
)
ON CONFLICT (id) DO UPDATE
SET title = EXCLUDED.title,
    summary = EXCLUDED.summary,
    low_level_features_json = EXCLUDED.low_level_features_json,
    similarity_groups_json = EXCLUDED.similarity_groups_json,
    interpretations_json = EXCLUDED.interpretations_json,
    report_json = EXCLUDED.report_json,
    markdown = EXCLUDED.markdown;

INSERT INTO possible_interpretations (
  id,
  report_id,
  target_type,
  target_id,
  name,
  confidence,
  evidence_json,
  alternative_names_json,
  uncertainty,
  created_at
)
VALUES
  (
    '60000000-0000-0000-0000-000000000001',
    '50000000-0000-0000-0000-000000000001',
    'similarity_group',
    'similarity_group_001',
    '克制空间感',
    0.72,
    '[
      {"inputId": "10000000-0000-0000-0000-000000000001", "reason": "低饱和室内空间"},
      {"inputId": "10000000-0000-0000-0000-000000000002", "reason": "空房间和回声意象"},
      {"inputId": "10000000-0000-0000-0000-000000000004", "reason": "没有人物经过"}
    ]'::jsonb,
    '["留白秩序", "低刺激空间"]'::jsonb,
    '也可能只是本次样本主题较集中。',
    '2026-05-15T09:16:00Z'
  ),
  (
    '60000000-0000-0000-0000-000000000002',
    '50000000-0000-0000-0000-000000000001',
    'report',
    '50000000-0000-0000-0000-000000000001',
    '弱叙事强氛围',
    0.67,
    '[
      {"inputId": "10000000-0000-0000-0000-000000000002", "reason": "文本像片段观察"},
      {"inputId": "10000000-0000-0000-0000-000000000004", "reason": "弱情节和静止描写"}
    ]'::jsonb,
    '["片段式观察", "氛围优先"]'::jsonb,
    '文本样本数量仍然偏少，需要更多输入验证。',
    '2026-05-15T09:16:30Z'
  )
ON CONFLICT (id) DO UPDATE
SET target_type = EXCLUDED.target_type,
    target_id = EXCLUDED.target_id,
    name = EXCLUDED.name,
    confidence = EXCLUDED.confidence,
    evidence_json = EXCLUDED.evidence_json,
    alternative_names_json = EXCLUDED.alternative_names_json,
    uncertainty = EXCLUDED.uncertainty;

INSERT INTO insights (
  id,
  report_id,
  interpretation_id,
  title,
  observation,
  evidence_json,
  interpretation,
  uncertainty,
  confidence,
  created_at
)
VALUES
  (
    '70000000-0000-0000-0000-000000000001',
    '50000000-0000-0000-0000-000000000001',
    '60000000-0000-0000-0000-000000000001',
    '你近期可能更容易被安静、低密度的结构吸引',
    '多个输入都出现低饱和、低元素密度和人物缺席。',
    '[
      {"inputId": "10000000-0000-0000-0000-000000000001", "feature": "low_saturation"},
      {"inputId": "10000000-0000-0000-0000-000000000002", "feature": "low_narrative_density"},
      {"inputId": "10000000-0000-0000-0000-000000000004", "feature": "person_absent"}
    ]'::jsonb,
    '这可能说明你现在更关注留白、秩序和克制的空间感。',
    '它不是心理诊断，只是对本次样本的审美结构观察。',
    0.72,
    '2026-05-15T09:17:00Z'
  ),
  (
    '70000000-0000-0000-0000-000000000002',
    '50000000-0000-0000-0000-000000000001',
    '60000000-0000-0000-0000-000000000002',
    '样本中有一种弱叙事、强氛围的倾向',
    '文字样本更强调状态、光线和空间，而不是明确事件。',
    '[
      {"inputId": "10000000-0000-0000-0000-000000000002", "feature": "slow_temporal_pace"},
      {"inputId": "10000000-0000-0000-0000-000000000004", "feature": "quiet_atmosphere"}
    ]'::jsonb,
    '这可能表示你对开放解释空间的作品更有耐心。',
    '如果后续样本加入人物或强情节内容，这条洞察可能会改变。',
    0.66,
    '2026-05-15T09:17:30Z'
  ),
  (
    '70000000-0000-0000-0000-000000000003',
    '50000000-0000-0000-0000-000000000001',
    NULL,
    '暖色样本更像局部变化，而不是整体偏好翻转',
    '第五个图片样本在色温上更暖，但仍保持低密度构图。',
    '[
      {"inputId": "10000000-0000-0000-0000-000000000005", "feature": "warm_temperature"},
      {"inputId": "10000000-0000-0000-0000-000000000005", "feature": "low_density"}
    ]'::jsonb,
    '它可能是当前审美里的局部调剂，而不是与前面样本完全相反的方向。',
    '单个暖色样本不能证明稳定偏好，需要后续样本继续观察。',
    0.61,
    '2026-05-15T09:18:00Z'
  )
ON CONFLICT (id) DO UPDATE
SET interpretation_id = EXCLUDED.interpretation_id,
    title = EXCLUDED.title,
    observation = EXCLUDED.observation,
    evidence_json = EXCLUDED.evidence_json,
    interpretation = EXCLUDED.interpretation,
    uncertainty = EXCLUDED.uncertainty,
    confidence = EXCLUDED.confidence;

INSERT INTO insight_feedback (id, user_id, insight_id, interpretation_id, rating, comment, created_at)
VALUES
  (
    '80000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '70000000-0000-0000-0000-000000000001',
    '60000000-0000-0000-0000-000000000001',
    'somewhat_me',
    '低密度和留白这一点比较准确。',
    '2026-05-15T09:20:00Z'
  ),
  (
    '80000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    '70000000-0000-0000-0000-000000000002',
    '60000000-0000-0000-0000-000000000002',
    'very_me',
    '确实更喜欢氛围先于情节。',
    '2026-05-15T09:21:00Z'
  )
ON CONFLICT (id) DO UPDATE
SET rating = EXCLUDED.rating,
    comment = EXCLUDED.comment,
    interpretation_id = EXCLUDED.interpretation_id;

INSERT INTO analysis_logs (
  id,
  job_id,
  step_id,
  status,
  model_name,
  prompt_version,
  latency_ms,
  error_type,
  error_message,
  created_at
)
VALUES
  (
    '90000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001',
    'load_inputs',
    'running',
    NULL,
    NULL,
    18,
    NULL,
    NULL,
    '2026-05-15T09:12:05Z'
  ),
  (
    '90000000-0000-0000-0000-000000000002',
    '40000000-0000-0000-0000-000000000001',
    'extract_low_level_features',
    'feature_extracting',
    'mock-vision-v1/mock-llm-v1',
    'image_features.extract.v1,text_features.extract.v1',
    420,
    NULL,
    NULL,
    '2026-05-15T09:12:35Z'
  ),
  (
    '90000000-0000-0000-0000-000000000003',
    '40000000-0000-0000-0000-000000000001',
    'generate_embeddings',
    'embedding_generating',
    'mock-embedding-v1',
    NULL,
    95,
    NULL,
    NULL,
    '2026-05-15T09:13:05Z'
  ),
  (
    '90000000-0000-0000-0000-000000000004',
    '40000000-0000-0000-0000-000000000001',
    'group_inputs_by_similarity',
    'similarity_grouping',
    'mock-similarity-v1',
    NULL,
    66,
    NULL,
    NULL,
    '2026-05-15T09:13:30Z'
  ),
  (
    '90000000-0000-0000-0000-000000000005',
    '40000000-0000-0000-0000-000000000001',
    'generate_report',
    'report_generating',
    'mock-llm-v1',
    'report.generate.v1',
    530,
    NULL,
    NULL,
    '2026-05-15T09:14:10Z'
  ),
  (
    '90000000-0000-0000-0000-000000000006',
    '40000000-0000-0000-0000-000000000001',
    'save_report_and_insights',
    'completed',
    NULL,
    NULL,
    44,
    NULL,
    NULL,
    '2026-05-15T09:14:30Z'
  )
ON CONFLICT (id) DO UPDATE
SET step_id = EXCLUDED.step_id,
    status = EXCLUDED.status,
    model_name = EXCLUDED.model_name,
    prompt_version = EXCLUDED.prompt_version,
    latency_ms = EXCLUDED.latency_ms,
    error_type = EXCLUDED.error_type,
    error_message = EXCLUDED.error_message;
