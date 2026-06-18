from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persistence import AgentActionLogModel, ObservationSessionModel
from app.repositories.memory_store import MemoryStore
from app.schemas.agent import AgentActionLog, AgentActionListResponse, ObservationQuestion, ObservationSession
from app.schemas.common import new_id, utc_now


def _session_from_model(row: ObservationSessionModel) -> ObservationSession:
    return ObservationSession(
        id=row.id,
        userId=row.user_id,
        status=row.status,
        triggerSource=row.trigger_source,
        period=row.period,
        summary=row.summary,
        questions=[ObservationQuestion.model_validate(item) for item in (row.questions_json or [])],
        evidenceRefs=list(row.evidence_refs_json or []),
        message=row.message,
        disclaimer=row.disclaimer,
        createdAt=row.created_at,
        finishedAt=row.finished_at,
    )


def _action_from_model(row: AgentActionLogModel) -> AgentActionLog:
    return AgentActionLog(
        id=row.id,
        userId=row.user_id,
        sessionId=row.session_id,
        stepIndex=row.step_index,
        toolName=row.tool_name,
        reason=row.reason,
        inputRefs=list(row.input_refs_json or []),
        outputRefs=list(row.output_refs_json or []),
        status=row.status,
        latencyMs=row.latency_ms,
        createdAt=row.created_at,
    )


class ObservationSessionRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save(self, session: ObservationSession) -> ObservationSession:
        self.store.observation_sessions[session.id] = session
        return session

    def get(self, session_id: str) -> ObservationSession | None:
        return self.store.observation_sessions.get(session_id)

    def get_for_user(self, user_id: str, session_id: str) -> ObservationSession | None:
        session = self.get(session_id)
        if session is None or session.user_id != user_id:
            return None
        return session


class AgentActionLogRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def append(self, action: AgentActionLog) -> AgentActionLog:
        self.store.agent_action_logs[action.id] = action
        return action

    def list_by_user(
        self,
        user_id: str,
        *,
        session_id: str | None = None,
        limit: int = 100,
    ) -> AgentActionListResponse:
        actions = [
            action
            for action in self.store.agent_action_logs.values()
            if action.user_id == user_id and (session_id is None or action.session_id == session_id)
        ]
        actions.sort(key=lambda item: (item.created_at, item.step_index))
        page = actions[:limit]
        return AgentActionListResponse(
            userId=user_id,
            actions=page,
            total=len(actions),
            sessionId=session_id,
        )


class DatabaseObservationSessionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, observation: ObservationSession) -> ObservationSession:
        existing = self.session.get(ObservationSessionModel, observation.id)
        payload = {
            "user_id": observation.user_id,
            "status": observation.status,
            "trigger_source": observation.trigger_source,
            "period": observation.period,
            "summary": observation.summary,
            "questions_json": [item.model_dump(by_alias=True) for item in observation.questions],
            "evidence_refs_json": observation.evidence_refs,
            "message": observation.message,
            "disclaimer": observation.disclaimer,
            "created_at": observation.created_at,
            "finished_at": observation.finished_at,
        }
        if existing is None:
            row = ObservationSessionModel(id=observation.id, **payload)
            self.session.add(row)
        else:
            for key, value in payload.items():
                setattr(existing, key, value)
        self.session.flush()
        return observation

    def get(self, session_id: str) -> ObservationSession | None:
        row = self.session.get(ObservationSessionModel, session_id)
        return _session_from_model(row) if row is not None else None

    def get_for_user(self, user_id: str, session_id: str) -> ObservationSession | None:
        row = self.session.get(ObservationSessionModel, session_id)
        if row is None or row.user_id != user_id:
            return None
        return _session_from_model(row)


class DatabaseAgentActionLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def append(self, action: AgentActionLog) -> AgentActionLog:
        row = AgentActionLogModel(
            id=action.id,
            user_id=action.user_id,
            session_id=action.session_id,
            step_index=action.step_index,
            tool_name=action.tool_name,
            reason=action.reason,
            input_refs_json=action.input_refs,
            output_refs_json=action.output_refs,
            status=action.status,
            latency_ms=action.latency_ms,
            created_at=action.created_at,
        )
        self.session.add(row)
        self.session.flush()
        return action

    def list_by_user(
        self,
        user_id: str,
        *,
        session_id: str | None = None,
        limit: int = 100,
    ) -> AgentActionListResponse:
        query = select(AgentActionLogModel).where(AgentActionLogModel.user_id == user_id)
        if session_id is not None:
            query = query.where(AgentActionLogModel.session_id == session_id)
        rows = self.session.scalars(
            query.order_by(AgentActionLogModel.created_at.asc(), AgentActionLogModel.step_index.asc())
        ).all()
        actions = [_action_from_model(row) for row in rows[:limit]]
        return AgentActionListResponse(
            userId=user_id,
            actions=actions,
            total=len(rows),
            sessionId=session_id,
        )


def new_observation_session(
    user_id: str,
    *,
    trigger_source: str,
    period: str | None,
) -> ObservationSession:
    now = utc_now()
    return ObservationSession(
        id=new_id("observation"),
        userId=user_id,
        status="running",
        triggerSource=trigger_source,
        period=period,
        createdAt=now,
    )


def new_agent_action(
    *,
    user_id: str,
    session_id: str,
    step_index: int,
    tool_name: str,
    reason: str,
    input_refs: list[str],
    output_refs: list[str],
    status: str,
    latency_ms: int | None,
) -> AgentActionLog:
    return AgentActionLog(
        id=new_id("agent_action"),
        userId=user_id,
        sessionId=session_id,
        stepIndex=step_index,
        toolName=tool_name,
        reason=reason,
        inputRefs=input_refs,
        outputRefs=output_refs,
        status=status,
        latencyMs=latency_ms,
        createdAt=utc_now(),
    )
