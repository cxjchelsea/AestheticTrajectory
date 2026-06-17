from app.schemas.feature import InputFeature
from app.schemas.knowledge_context import AestheticKnowledgeContext
from app.services.aesthetic_knowledge_retrieval import build_aesthetic_knowledge_context


def retrieve_aesthetic_knowledge(features: list[InputFeature]) -> AestheticKnowledgeContext:
    return build_aesthetic_knowledge_context(features)
