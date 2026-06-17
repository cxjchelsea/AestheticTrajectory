DO $$
DECLARE
  reset_tables text[] := ARRAY[
    'profile_evidence',
    'profile_items',
    'user_profiles',
    'insight_feedback',
    'analysis_logs',
    'insights',
    'possible_interpretations',
    'aesthetic_reports',
    'embedding_records',
    'input_features',
    'analysis_jobs',
    'aesthetic_inputs',
    'users'
  ];
  existing_tables text;
BEGIN
  SELECT string_agg(format('%I.%I', table_schema, table_name), ', ' ORDER BY array_position(reset_tables, table_name))
  INTO existing_tables
  FROM information_schema.tables
  WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND table_name = ANY(reset_tables);

  IF existing_tables IS NULL THEN
    RAISE NOTICE 'No resettable business tables found.';
  ELSE
    EXECUTE 'TRUNCATE TABLE ' || existing_tables || ' RESTART IDENTITY CASCADE';
    RAISE NOTICE 'Reset business tables: %', existing_tables;
  END IF;
END $$;
