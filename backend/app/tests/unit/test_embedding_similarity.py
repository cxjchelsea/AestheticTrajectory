import pytest

from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse
from app.workflows.steps.build_embedding_text import build_embedding_text
from app.workflows.steps.cluster_inputs import build_similarity_groups
from app.workflows.steps.generate_embeddings import generate_embeddings
from app.workflows.steps.similarity import cosine_similarity


class StaticEmbeddingClient:
    vector_dimension = 2

    @property
    def model_name(self) -> str:
        return "static-test-embedding"

    def embed(self, text: str) -> list[float]:
        if "quiet" in text:
            return [1.0, 0.0]
        return [0.0, 1.0]


def test_build_embedding_text_uses_feature_summary_for_text_input() -> None:
    input_record = AestheticInputResponse(
        id="input_001",
        userId="user_anonymous",
        type="text",
        contentText="quiet room",
        fileUrl=None,
        source="test",
        title="Quiet room",
        description="low density",
        createdAt="2026-06-16T00:00:00Z",
    )
    feature = _feature("input_001")

    embedding_text = build_embedding_text(input_record, feature)

    assert "标题：Quiet room" in embedding_text
    assert "正文：quiet room" in embedding_text
    assert "density=low" in embedding_text


def test_generate_embeddings_skips_empty_embedding_text() -> None:
    input_record = AestheticInputResponse(
        id="input_empty",
        userId="user_anonymous",
        type="text",
        contentText=None,
        fileUrl=None,
        source="test",
        title=None,
        description=None,
        createdAt="2026-06-16T00:00:00Z",
    )

    embeddings = generate_embeddings([input_record], client=StaticEmbeddingClient())

    assert embeddings == {}


def test_cosine_similarity_validates_vector_shape() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)

    with pytest.raises(ValueError, match="same dimension"):
        cosine_similarity([1.0], [1.0, 0.0])

    with pytest.raises(ValueError, match="non-zero"):
        cosine_similarity([0.0, 0.0], [1.0, 0.0])


def test_build_similarity_groups_uses_threshold_and_common_features() -> None:
    input_ids = ["input_001", "input_002", "input_003"]
    features = [_feature(input_id) for input_id in input_ids]
    embeddings = {
        "input_001": [1.0, 0.0],
        "input_002": [0.99, 0.01],
        "input_003": [0.0, 1.0],
    }

    groups = build_similarity_groups(input_ids, features, embeddings, similarity_threshold=0.82)

    assert len(groups) == 1
    assert groups[0].input_ids == ["input_001", "input_002"]
    assert "density:low" in groups[0].common_features
    assert "不代表长期偏好或绝对分类" in groups[0].uncertainty


def test_build_similarity_groups_skips_when_sample_count_is_too_small() -> None:
    groups = build_similarity_groups(
        ["input_001", "input_002"],
        [_feature("input_001"), _feature("input_002")],
        {"input_001": [1.0, 0.0], "input_002": [1.0, 0.0]},
    )

    assert groups == []


def _feature(input_id: str) -> InputFeature:
    return InputFeature(
        inputId=input_id,
        featureType="text",
        lowLevelFeatures={
            "density": FeatureSignal(value="low", confidence=0.8, evidence=["low density"]),
            "saturation": FeatureSignal(value="low", confidence=0.7, evidence=["low saturation"]),
        },
        sampleEvidence=["quiet evidence"],
        promptVersion="text_features.extract.v1",
        modelName="test-feature-extractor",
    )
