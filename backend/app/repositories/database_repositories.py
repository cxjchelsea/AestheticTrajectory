from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    AestheticInputModel,
    AestheticReportModel,
    AnalysisJobModel,
    AnalysisLogModel,
    EmbeddingRecordModel,
    InputFeatureModel,
    InsightFeedbackModel,
    InsightModel,
    PossibleInterpretationModel,
    ProfileEvidenceModel,
    ProfileItemModel,
    UserProfileModel,
    UserModel,
)
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.analysis_log import AnalysisLogRecord
from app.schemas.common import utc_now
from app.schemas.embedding import EmbeddingRecord
from app.schemas.feature import InputFeature
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.input import AestheticInputResponse
from app.schemas.profile import ProfileResponse
from app.schemas.report import ReportHistoryResponse, ReportResponse, ReportSummary
from app.services.profile_builder import build_profile_from_sources


class DatabaseInputRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, input_record: AestheticInputResponse) -> AestheticInputResponse:
        self._ensure_user(input_record.user_id, input_record.created_at)
        self.session.merge(
            AestheticInputModel(
                id=input_record.id,
                user_id=input_record.user_id,
                type=input_record.type,
                content_text=input_record.content_text,
                file_url=input_record.file_url,
                source=input_record.source,
                title=input_record.title,
                description=input_record.description,
                created_at=input_record.created_at,
                updated_at=input_record.created_at,
            )
        )
        return input_record

    def get_many(self, input_ids: list[str]) -> list[AestheticInputResponse]:
        if not input_ids:
            return []
        rows = self.session.scalars(
            select(AestheticInputModel).where(AestheticInputModel.id.in_(input_ids))
        ).all()
        by_id = {row.id: _input_from_model(row) for row in rows}
        return [by_id[input_id] for input_id in input_ids if input_id in by_id]

    def _ensure_user(self, user_id: str, now: datetime) -> None:
        if self.session.get(UserModel, user_id) is None:
            try:
                self.session.add(
                    UserModel(
                        id=user_id,
                        anonymous_id=user_id,
                        created_at=now,
                        updated_at=now,
                    )
                )
                self.session.flush()
            except IntegrityError:
                self.session.rollback()
                if self.session.get(UserModel, user_id) is None:
                    raise


class DatabaseAnalysisJobRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, job: AnalysisJobResponse) -> AnalysisJobResponse:
        self.session.merge(
            AnalysisJobModel(
                id=job.id,
                user_id=job.user_id,
                status=job.status,
                input_count=job.input_count,
                error_message=job.error_message,
                report_id=job.report_id,
                created_at=job.created_at,
                started_at=job.started_at,
                finished_at=job.finished_at,
            )
        )
        self.session.flush()
        return job

    def get(self, job_id: str) -> AnalysisJobResponse | None:
        row = self.session.get(AnalysisJobModel, job_id)
        if row is None:
            return None
        return AnalysisJobResponse(
            id=row.id,
            userId=row.user_id,
            status=row.status,
            inputCount=row.input_count,
            errorMessage=row.error_message,
            reportId=row.report_id,
            createdAt=row.created_at,
            startedAt=row.started_at,
            finishedAt=row.finished_at,
        )


class DatabaseFeatureRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_many(self, features: list[InputFeature]) -> list[InputFeature]:
        now = utc_now()
        for feature in features:
            self.session.merge(
                InputFeatureModel(
                    id=f"feature_{feature.input_id}",
                    input_id=feature.input_id,
                    feature_type=feature.feature_type,
                    model_name=feature.model_name,
                    prompt_version=feature.prompt_version,
                    feature_json=feature.model_dump(mode="json", by_alias=True),
                    summary=", ".join(
                        f"{name}={signal.value}" for name, signal in feature.low_level_features.items()
                    ),
                    created_at=now,
                )
            )
        return features


class DatabaseEmbeddingRecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_many(self, records: list[EmbeddingRecord]) -> list[EmbeddingRecord]:
        for record in records:
            self.session.merge(
                EmbeddingRecordModel(
                    id=record.id,
                    owner_type=record.owner_type,
                    owner_id=record.owner_id,
                    collection_name=record.collection_name,
                    chroma_id=record.chroma_id,
                    model_name=record.model_name,
                    vector_dimension=record.vector_dimension,
                    created_at=record.created_at,
                )
            )
        return records


class DatabaseReportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, report: ReportResponse, user_id: str | None = None, job_id: str | None = None) -> ReportResponse:
        report_json = report.model_dump(mode="json", by_alias=True)
        self.session.merge(
            AestheticReportModel(
                id=report.report_id,
                user_id=user_id,
                job_id=job_id,
                title=report.title,
                summary=report.summary,
                low_level_features_json=report_json["lowLevelFeatures"],
                similarity_groups_json=report_json["similarityGroups"],
                interpretations_json=report_json["possibleInterpretations"],
                report_json=report_json,
                markdown=None,
                created_at=utc_now(),
            )
        )
        for interpretation in report.possible_interpretations:
            self.session.merge(
                PossibleInterpretationModel(
                    id=interpretation.id,
                    report_id=report.report_id,
                    target_type="report",
                    target_id=report.report_id,
                    name=interpretation.name,
                    confidence=interpretation.confidence,
                    evidence_json=interpretation.evidence_refs,
                    alternative_names_json=[],
                    uncertainty=interpretation.uncertainty,
                    created_at=utc_now(),
                )
            )
        for insight in report.insights:
            self.session.merge(
                InsightModel(
                    id=insight.insight_id,
                    report_id=report.report_id,
                    interpretation_id=report.possible_interpretations[0].id
                    if report.possible_interpretations
                    else None,
                    title=insight.title,
                    observation=insight.observation,
                    evidence_json=insight.evidence_refs,
                    interpretation=insight.interpretation,
                    uncertainty=insight.uncertainty,
                    confidence=insight.confidence,
                    created_at=utc_now(),
                )
            )
        return report

    def get(self, report_id: str) -> ReportResponse | None:
        row = self.session.get(AestheticReportModel, report_id)
        if row is None:
            return None
        return ReportResponse.model_validate(row.report_json)

    def list_by_user(self, user_id: str, limit: int, offset: int) -> ReportHistoryResponse:
        total = self.session.scalar(
            select(func.count()).select_from(AestheticReportModel).where(AestheticReportModel.user_id == user_id)
        )
        rows = self.session.execute(
            select(AestheticReportModel, AnalysisJobModel.input_count)
            .outerjoin(AnalysisJobModel, AestheticReportModel.job_id == AnalysisJobModel.id)
            .where(AestheticReportModel.user_id == user_id)
            .order_by(AestheticReportModel.created_at.desc(), AestheticReportModel.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return ReportHistoryResponse(
            reports=[
                ReportSummary(
                    reportId=report.id,
                    jobId=report.job_id,
                    title=report.title,
                    summary=report.summary,
                    inputCount=input_count or 0,
                    createdAt=report.created_at,
                )
                for report, input_count in rows
            ],
            total=total or 0,
            limit=limit,
            offset=offset,
        )


class DatabaseFeedbackRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def insight_exists(self, insight_id: str) -> bool:
        return self.session.get(InsightModel, insight_id) is not None

    def get_for_target(self, user_id: str, insight_id: str) -> InsightFeedbackResponse | None:
        row = self.session.scalars(
            select(InsightFeedbackModel)
            .where(
                InsightFeedbackModel.user_id == user_id,
                InsightFeedbackModel.insight_id == insight_id,
            )
            .order_by(InsightFeedbackModel.created_at.desc(), InsightFeedbackModel.id.desc())
        ).first()
        if row is None:
            return None
        return InsightFeedbackResponse(
            id=row.id,
            userId=row.user_id,
            insightId=row.insight_id,
            interpretationId=row.interpretation_id,
            rating=row.rating,
            comment=row.comment,
            createdAt=row.created_at,
        )

    def save(self, feedback: InsightFeedbackResponse) -> InsightFeedbackResponse:
        existing = self.session.scalars(
            select(InsightFeedbackModel).where(
                InsightFeedbackModel.user_id == feedback.user_id,
                InsightFeedbackModel.insight_id == feedback.insight_id,
            )
        ).all()
        for row in existing:
            if row.id != feedback.id:
                self.session.delete(row)
        self.session.merge(
            InsightFeedbackModel(
                id=feedback.id,
                user_id=feedback.user_id,
                insight_id=feedback.insight_id,
                interpretation_id=feedback.interpretation_id,
                rating=feedback.rating,
                comment=feedback.comment,
                created_at=feedback.created_at,
            )
        )
        self.session.flush()
        return feedback


class DatabaseProfileRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_build(self, user_id: str) -> ProfileResponse:
        reports = [
            ReportResponse.model_validate(row.report_json)
            for row in self.session.scalars(
                select(AestheticReportModel)
                .where(AestheticReportModel.user_id == user_id)
                .order_by(AestheticReportModel.created_at.asc(), AestheticReportModel.id.asc())
            ).all()
        ]
        feedback = [
            InsightFeedbackResponse(
                id=row.id,
                userId=row.user_id,
                insightId=row.insight_id,
                interpretationId=row.interpretation_id,
                rating=row.rating,
                comment=row.comment,
                createdAt=row.created_at,
            )
            for row in self.session.scalars(
                select(InsightFeedbackModel)
                .where(InsightFeedbackModel.user_id == user_id)
                .order_by(InsightFeedbackModel.created_at.asc(), InsightFeedbackModel.id.asc())
            ).all()
        ]
        profile = build_profile_from_sources(user_id, reports, feedback)
        self._replace_profile(user_id, profile)
        return profile

    def _replace_profile(self, user_id: str, response: ProfileResponse) -> None:
        existing_profile_ids = [
            row.id for row in self.session.scalars(select(UserProfileModel).where(UserProfileModel.user_id == user_id)).all()
        ]
        if existing_profile_ids:
            existing_item_ids = [
                row.id
                for row in self.session.scalars(
                    select(ProfileItemModel).where(ProfileItemModel.profile_id.in_(existing_profile_ids))
                ).all()
            ]
            if existing_item_ids:
                self.session.execute(delete(ProfileEvidenceModel).where(ProfileEvidenceModel.profile_item_id.in_(existing_item_ids)))
            self.session.execute(delete(ProfileItemModel).where(ProfileItemModel.profile_id.in_(existing_profile_ids)))
            self.session.execute(delete(UserProfileModel).where(UserProfileModel.id.in_(existing_profile_ids)))

        if response.profile is None:
            self.session.flush()
            return

        now = response.profile.updated_at
        self.session.add(
            UserProfileModel(
                id=response.profile.id,
                user_id=user_id,
                summary=response.profile.summary,
                version=response.profile.version,
                created_at=now,
                updated_at=now,
            )
        )
        self.session.flush()
        for item in response.profile.items:
            self.session.add(
                ProfileItemModel(
                    id=item.id,
                    profile_id=response.profile.id,
                    key=item.key,
                    label=item.label,
                    status=item.status,
                    weight=item.weight,
                    confidence=item.confidence,
                    source_count=item.source_count,
                    last_seen_at=item.last_seen_at,
                    created_at=now,
                    updated_at=now,
                )
            )
        self.session.flush()

        for item in response.profile.items:
            for evidence in item.evidence:
                self.session.add(
                    ProfileEvidenceModel(
                        id=evidence.id,
                        profile_item_id=item.id,
                        evidence_type=evidence.evidence_type,
                        evidence_id=evidence.evidence_id,
                        direction=evidence.direction,
                        weight_delta=evidence.weight_delta,
                        note=evidence.note,
                        created_at=evidence.created_at,
                    )
                )
        self.session.flush()


class DatabaseAnalysisLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, log: AnalysisLogRecord) -> AnalysisLogRecord:
        self.session.merge(
            AnalysisLogModel(
                id=log.id,
                job_id=log.job_id,
                step_id=log.step_id,
                status=log.status,
                model_name=log.model_name,
                prompt_version=log.prompt_version,
                latency_ms=log.latency_ms,
                error_type=log.error_type,
                error_message=log.error_message,
                started_at=log.started_at,
                finished_at=log.finished_at,
                created_at=log.created_at,
            )
        )
        return log

    def get_for_job(self, job_id: str) -> list[AnalysisLogRecord]:
        rows = self.session.scalars(
            select(AnalysisLogModel).where(AnalysisLogModel.job_id == job_id)
        ).all()
        return [
            AnalysisLogRecord(
                id=row.id,
                jobId=row.job_id,
                stepId=row.step_id,
                status=row.status,
                modelName=row.model_name,
                promptVersion=row.prompt_version,
                latencyMs=row.latency_ms,
                errorType=row.error_type,
                errorMessage=row.error_message,
                startedAt=row.started_at,
                finishedAt=row.finished_at,
                createdAt=row.created_at,
            )
            for row in rows
        ]


def _input_from_model(row: AestheticInputModel) -> AestheticInputResponse:
    return AestheticInputResponse(
        id=row.id,
        userId=row.user_id,
        type=row.type,
        contentText=row.content_text,
        fileUrl=row.file_url,
        source=row.source,
        title=row.title,
        description=row.description,
        createdAt=row.created_at,
    )
