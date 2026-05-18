DO $$
BEGIN
  IF to_regclass('public.insight_feedback') IS NOT NULL THEN
    DELETE FROM insight_feedback;
  END IF;

  IF to_regclass('public.analysis_logs') IS NOT NULL THEN
    DELETE FROM analysis_logs;
  END IF;

  IF to_regclass('public.insights') IS NOT NULL THEN
    DELETE FROM insights;
  END IF;

  IF to_regclass('public.possible_interpretations') IS NOT NULL THEN
    DELETE FROM possible_interpretations;
  END IF;

  IF to_regclass('public.aesthetic_reports') IS NOT NULL THEN
    DELETE FROM aesthetic_reports;
  END IF;

  IF to_regclass('public.embedding_records') IS NOT NULL THEN
    DELETE FROM embedding_records;
  END IF;

  IF to_regclass('public.input_features') IS NOT NULL THEN
    DELETE FROM input_features;
  END IF;

  IF to_regclass('public.analysis_jobs') IS NOT NULL THEN
    DELETE FROM analysis_jobs;
  END IF;

  IF to_regclass('public.aesthetic_inputs') IS NOT NULL THEN
    DELETE FROM aesthetic_inputs;
  END IF;

  IF to_regclass('public.users') IS NOT NULL THEN
    DELETE FROM users;
  END IF;
END $$;
