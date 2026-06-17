from app.schemas.feature import InputFeature
from app.schemas.history_context import PersonalHistoryContext
from app.services.personal_history_retrieval import build_personal_history_context


def retrieve_personal_history(
    user_id: str,
    report_id: str,
    features: list[InputFeature],
    report_repository,
    feedback_repository,
) -> PersonalHistoryContext:
    historical_reports = report_repository.list_recent_by_user(user_id, limit=10)
    feedback = feedback_repository.list_by_user(user_id)
    return build_personal_history_context(report_id, features, historical_reports, feedback)
