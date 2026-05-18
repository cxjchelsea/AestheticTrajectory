from app.ai.mock.mock_feature_extractor import MockFeatureExtractor
from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse


def extract_features(inputs: list[AestheticInputResponse]) -> list[InputFeature]:
    extractor = MockFeatureExtractor()
    return [extractor.extract(input_record, index) for index, input_record in enumerate(inputs)]
