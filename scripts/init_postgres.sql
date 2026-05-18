CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  anonymous_id TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS aesthetic_inputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('image', 'text')),
  content_text TEXT,
  file_url TEXT,
  source TEXT NOT NULL DEFAULT 'manual',
  title TEXT,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (
    (type = 'image' AND file_url IS NOT NULL)
    OR
    (type = 'text' AND content_text IS NOT NULL)
  )
);

CREATE TABLE IF NOT EXISTS input_features (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  input_id UUID NOT NULL REFERENCES aesthetic_inputs(id) ON DELETE CASCADE,
  feature_type TEXT NOT NULL CHECK (feature_type IN ('image', 'text')),
  model_name TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  feature_json JSONB NOT NULL,
  summary TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (jsonb_typeof(feature_json) = 'object'),
  CHECK (feature_json ? 'lowLevelFeatures'),
  CHECK (jsonb_typeof(feature_json -> 'lowLevelFeatures') = 'object'),
  CHECK (
    NOT (feature_json ? 'sampleEvidence')
    OR jsonb_typeof(feature_json -> 'sampleEvidence') = 'array'
  )
);

CREATE TABLE IF NOT EXISTS embedding_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_type TEXT NOT NULL CHECK (owner_type IN ('input')),
  owner_id UUID NOT NULL,
  collection_name TEXT NOT NULL,
  chroma_id TEXT NOT NULL UNIQUE,
  model_name TEXT NOT NULL,
  vector_dimension INTEGER NOT NULL CHECK (vector_dimension > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analysis_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (
    status IN (
      'created',
      'queued',
      'running',
      'feature_extracting',
      'embedding_generating',
      'vector_writing',
      'similarity_grouping',
      'interpreting',
      'report_generating',
      'completed',
      'failed',
      'partial_failed',
      'cancelled'
    )
  ),
  input_count INTEGER NOT NULL CHECK (input_count >= 0),
  error_message TEXT,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS aesthetic_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  low_level_features_json JSONB NOT NULL,
  similarity_groups_json JSONB NOT NULL,
  interpretations_json JSONB NOT NULL,
  report_json JSONB NOT NULL,
  markdown TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (jsonb_typeof(low_level_features_json) IN ('array', 'object')),
  CHECK (jsonb_typeof(similarity_groups_json) = 'array'),
  CHECK (jsonb_typeof(interpretations_json) = 'array'),
  CHECK (jsonb_typeof(report_json) = 'object'),
  CHECK (report_json ? 'similarityGroups')
);

CREATE TABLE IF NOT EXISTS possible_interpretations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID NOT NULL REFERENCES aesthetic_reports(id) ON DELETE CASCADE,
  target_type TEXT NOT NULL CHECK (target_type IN ('report', 'similarity_group', 'input')),
  target_id TEXT NOT NULL,
  name TEXT NOT NULL,
  confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  evidence_json JSONB NOT NULL,
  alternative_names_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  uncertainty TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (jsonb_typeof(evidence_json) = 'array'),
  CHECK (jsonb_typeof(alternative_names_json) = 'array')
);

CREATE TABLE IF NOT EXISTS insights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID NOT NULL REFERENCES aesthetic_reports(id) ON DELETE CASCADE,
  interpretation_id UUID REFERENCES possible_interpretations(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  observation TEXT NOT NULL,
  evidence_json JSONB NOT NULL,
  interpretation TEXT NOT NULL,
  uncertainty TEXT NOT NULL,
  confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (jsonb_typeof(evidence_json) = 'array')
);

CREATE TABLE IF NOT EXISTS insight_feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  insight_id UUID NOT NULL REFERENCES insights(id) ON DELETE CASCADE,
  interpretation_id UUID REFERENCES possible_interpretations(id) ON DELETE SET NULL,
  rating TEXT NOT NULL CHECK (rating IN ('not_me', 'unsure', 'somewhat_me', 'very_me')),
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analysis_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID NOT NULL REFERENCES analysis_jobs(id) ON DELETE CASCADE,
  step_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK (
    status IN (
      'created',
      'queued',
      'running',
      'feature_extracting',
      'embedding_generating',
      'vector_writing',
      'similarity_grouping',
      'interpreting',
      'report_generating',
      'completed',
      'failed',
      'partial_failed',
      'cancelled'
    )
  ),
  model_name TEXT,
  prompt_version TEXT,
  latency_ms INTEGER CHECK (latency_ms IS NULL OR latency_ms >= 0),
  error_type TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_aesthetic_inputs_user_id ON aesthetic_inputs(user_id);
CREATE INDEX IF NOT EXISTS idx_input_features_input_id ON input_features(input_id);
CREATE INDEX IF NOT EXISTS idx_embedding_records_owner ON embedding_records(owner_type, owner_id);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_user_id ON analysis_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_aesthetic_reports_job_id ON aesthetic_reports(job_id);
CREATE INDEX IF NOT EXISTS idx_possible_interpretations_report_id ON possible_interpretations(report_id);
CREATE INDEX IF NOT EXISTS idx_insights_report_id ON insights(report_id);
CREATE INDEX IF NOT EXISTS idx_insight_feedback_insight_id ON insight_feedback(insight_id);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_job_id ON analysis_logs(job_id);
