from app.schemas.feature import InputFeature
from app.schemas.knowledge_context import AestheticKnowledgeContext
from app.services.aesthetic_knowledge_retrieval import build_aesthetic_knowledge_context
from app.vector_store.knowledge_vector_store import get_knowledge_vector_store


def retrieve_aesthetic_knowledge(
    features: list[InputFeature],
    *,
    graph_repository=None,
) -> AestheticKnowledgeContext:
    try:
        knowledge_vector_store = get_knowledge_vector_store()
    except Exception as exc:
        context = build_aesthetic_knowledge_context(
            features,
            graph_repository=graph_repository,
            knowledge_vector_store=None,
        )
        if context.retrieval_meta is None:
            return context
        return context.model_copy(
            update={
                "retrieval_meta": context.retrieval_meta.model_copy(
                    update={
                        "vector_path": "failed",
                        "vector_error_message": str(exc),
                    }
                )
            }
        )

    return build_aesthetic_knowledge_context(
        features,
        graph_repository=graph_repository,
        knowledge_vector_store=knowledge_vector_store,
    )
