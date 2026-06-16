from app.ai.feature_extractor import FeatureExtractor
from app.ai.mock.mock_feature_extractor import MockFeatureExtractor
from app.ai.validators.prompt_output_validator import validate_input_feature
from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse


def extract_features(
    inputs: list[AestheticInputResponse],
    extractor: FeatureExtractor | None = None,
) -> list[InputFeature]:
    active_extractor = extractor or MockFeatureExtractor()
    return [
        validate_input_feature(active_extractor.extract(input_record, index))
        for index, input_record in enumerate(inputs)
    ]
