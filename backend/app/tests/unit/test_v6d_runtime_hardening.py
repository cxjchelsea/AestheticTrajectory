from pathlib import Path


def _env_example_values() -> dict[str, str]:
    env_path = Path(__file__).resolve().parents[3] / ".env.example"
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def test_v6d_env_example_matches_runtime_defaults() -> None:
    from app.core.config import settings

    values = _env_example_values()

    assert values["IMAGE_FEATURE_RUNTIME"] == settings.image_feature_runtime
    assert values["IMAGE_FEATURE_MODEL"] == settings.image_feature_model
    assert values["IMAGE_FEATURE_TIMEOUT_SECONDS"] == str(settings.image_feature_timeout_seconds)
    assert values["MUSIC_FEATURE_RUNTIME"] == settings.music_feature_runtime
    assert values["VIDEO_FEATURE_RUNTIME"] == settings.video_feature_runtime
    assert values["REPORT_LLM_RUNTIME"] == settings.report_llm_runtime
    assert values["EMBEDDING_RUNTIME"] == settings.embedding_runtime
    assert values["CHROMA_ENABLED"].lower() == "false"


def test_v6d_default_pytest_runtime_uses_no_external_services() -> None:
    from app.core.config import settings

    assert settings.repository_backend == "memory"
    assert settings.embedding_runtime == "mock"
    assert settings.chroma_enabled is False
    assert settings.report_llm_runtime == "mock"
    assert settings.image_feature_runtime == "mock"
    assert settings.music_feature_runtime == "metadata_only"
    assert settings.video_feature_runtime == "metadata_only"


def test_v6d_debug_boundary_lists_all_multimodal_runtimes() -> None:
    from app.services.analysis_job_service import _mock_usage, _runtime_boundary_status

    components = {item.component: item for item in _mock_usage()}

    assert components["MockImageFeatureExtractor"].status == "enabled"
    assert components["MetadataOnlyAudioMusicFeatureExtractor"].status == "disabled"
    assert components["MetadataOnlyVideoFeatureExtractor"].status == "disabled"

    _status, message = _runtime_boundary_status()
    assert "IMAGE_FEATURE_RUNTIME=mock" in message
    assert "MUSIC_FEATURE_RUNTIME=metadata_only" in message
    assert "VIDEO_FEATURE_RUNTIME=metadata_only" in message
