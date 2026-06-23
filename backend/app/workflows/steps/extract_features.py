from app.ai.factory import get_feature_extractor
from app.ai.feature_extractor import FeatureExtractor
from app.ai.validators.prompt_output_validator import validate_input_feature
from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse


def extract_features(
    inputs: list[AestheticInputResponse],
    extractor: FeatureExtractor | None = None,
) -> list[InputFeature]:
    active_extractor = extractor or get_feature_extractor()
    return [
        validate_input_feature(active_extractor.extract(input_record, index))
        for index, input_record in enumerate(inputs)
    ]
