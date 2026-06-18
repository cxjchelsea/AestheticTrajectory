from app.agent.tool_registry import (
    AgentToolRegistry,
    MockObservationPlanner,
    ObservationRunState,
    ToolContext,
    build_observation_output,
    run_tool_step,
    MAX_TOOL_STEPS,
)
from app.repositories.agent_repository import (
    AgentActionLogRepository,
    ObservationSessionRepository,
    new_agent_action,
    new_observation_session,
)
from app.schemas.agent import OBSERVATION_DISCLAIMER, CreateObservationRequest, ObservationSession


class ObservationAgentService:
    def __init__(
        self,
        session_repository: ObservationSessionRepository,
        action_repository: AgentActionLogRepository,
        tool_context: ToolContext,
        *,
        registry: AgentToolRegistry | None = None,
        planner: MockObservationPlanner | None = None,
    ) -> None:
        self.session_repository = session_repository
        self.action_repository = action_repository
        self.tool_context = tool_context
        self.registry = registry or AgentToolRegistry()
        self.planner = planner or MockObservationPlanner()

    def run_observation(self, user_id: str, request: CreateObservationRequest) -> ObservationSession:
        session = new_observation_session(
            user_id,
            trigger_source=request.trigger_source,
            period=request.period,
        )
        self.session_repository.save(session)

        state = ObservationRunState(user_id=user_id, period=request.period)
        step_index = 0

        while step_index < MAX_TOOL_STEPS:
            planned, result, latency_ms = run_tool_step(
                registry=self.registry,
                planner=self.planner,
                context=self.tool_context,
                state=state,
                step_index=step_index,
            )
            if planned is None:
                break

            status = "success" if result is not None else "failed"
            output_refs = result.output_refs if result is not None else []
            self.action_repository.append(
                new_agent_action(
                    user_id=user_id,
                    session_id=session.id,
                    step_index=step_index,
                    tool_name=planned.tool_name,
                    reason=planned.reason,
                    input_refs=[f"{key}={value}" for key, value in planned.params.items()] or [f"userId={user_id}"],
                    output_refs=output_refs,
                    status=status,
                    latency_ms=latency_ms,
                )
            )
            step_index += 1

            if planned.tool_name == "list_reports" and not state.report_ids:
                break

        summary, questions, abstain_message = build_observation_output(state)
        from app.schemas.common import utc_now

        if abstain_message:
            finished = session.model_copy(
                update={
                    "status": "abstained",
                    "message": abstain_message,
                    "finished_at": utc_now(),
                }
            )
        else:
            finished = session.model_copy(
                update={
                    "status": "completed",
                    "summary": summary,
                    "questions": questions,
                    "evidence_refs": state.evidence_refs,
                    "finished_at": utc_now(),
                    "disclaimer": OBSERVATION_DISCLAIMER,
                }
            )

        self.session_repository.save(finished)
        return finished
