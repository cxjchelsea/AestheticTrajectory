from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from app.repositories.external_import_repository import ExternalImportRepository
from app.schemas.agent import OBSERVATION_DISCLAIMER, ObservationQuestion
from app.schemas.timeline import TimelineSummaryPeriod
from app.services.knowledge_graph_query import KnowledgeGraphQueryService
from app.services.profile_service import ProfileService
from app.services.report_service import ReportService
from app.services.timeline_service import TimelineService


READ_ONLY_TOOLS = frozenset(
    {
        "list_reports",
        "get_report",
        "get_timeline_summary",
        "list_timeline_events",
        "get_profile",
        "get_knowledge_graph",
        "list_knowledge_chunks",
        "list_external_context",
    }
)


@dataclass
class ToolExecutionResult:
    payload: dict[str, Any]
    output_refs: list[str]


@dataclass
class ToolContext:
    report_service: ReportService
    timeline_service: TimelineService
    profile_service: ProfileService
    knowledge_service: KnowledgeGraphQueryService
    external_import_repository: ExternalImportRepository


@dataclass
class ObservationRunState:
    user_id: str
    period: TimelineSummaryPeriod = "week"
    report_ids: list[str] = field(default_factory=list)
    latest_report_id: str | None = None
    latest_report_title: str | None = None
    timeline_event_ids: list[str] = field(default_factory=list)
    profile_item_ids: list[str] = field(default_factory=list)
    external_item_ids: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    executed_tools: set[str] = field(default_factory=set)
    timeline_highlight_count: int = 0

    def add_refs(self, refs: list[str]) -> None:
        for ref in refs:
            if ref and ref not in self.evidence_refs:
                self.evidence_refs.append(ref)


class AgentToolRegistry:
    def execute(
        self,
        tool_name: str,
        user_id: str,
        params: dict[str, Any],
        context: ToolContext,
        state: ObservationRunState,
    ) -> ToolExecutionResult:
        if tool_name not in READ_ONLY_TOOLS:
            raise ValueError(f"Unsupported tool: {tool_name}")

        if tool_name == "list_reports":
            history = context.report_service.list_user_reports(user_id, limit=5, offset=0)
            report_ids = [item.report_id for item in history.reports]
            state.report_ids = report_ids
            if report_ids:
                state.latest_report_id = report_ids[0]
                state.latest_report_title = history.reports[0].title
            state.add_refs(report_ids)
            return ToolExecutionResult(
                payload={"total": history.total, "reportIds": report_ids},
                output_refs=report_ids,
            )

        if tool_name == "get_report":
            report_id = params.get("reportId") or state.latest_report_id
            if not report_id:
                return ToolExecutionResult(payload={"found": False}, output_refs=[])
            report = context.report_service.get_report(report_id)
            if report is None:
                return ToolExecutionResult(payload={"found": False}, output_refs=[])
            insight_ids = [insight.insight_id for insight in report.insights]
            refs = [report.report_id, *insight_ids]
            state.latest_report_id = report.report_id
            state.latest_report_title = report.title
            state.add_refs(refs)
            return ToolExecutionResult(
                payload={
                    "reportId": report.report_id,
                    "title": report.title,
                    "summary": report.summary,
                    "insightCount": len(report.insights),
                },
                output_refs=refs,
            )

        if tool_name == "get_timeline_summary":
            period = params.get("period") or state.period
            summary = context.timeline_service.get_summary(user_id, period)
            highlight_refs: list[str] = []
            for highlight in summary.highlights:
                highlight_refs.extend(highlight.evidence_refs)
            state.timeline_highlight_count = len(summary.highlights)
            state.add_refs(highlight_refs)
            return ToolExecutionResult(
                payload={
                    "period": period,
                    "summary": summary.summary_text,
                    "highlightCount": len(summary.highlights),
                },
                output_refs=highlight_refs,
            )

        if tool_name == "list_timeline_events":
            timeline = context.timeline_service.list_timeline(user_id, limit=5, offset=0)
            event_ids = [event.id for event in timeline.events]
            state.timeline_event_ids = event_ids
            for event in timeline.events:
                state.add_refs([event.id, *event.evidence.evidence_refs])
            return ToolExecutionResult(
                payload={"total": timeline.total, "eventIds": event_ids},
                output_refs=event_ids,
            )

        if tool_name == "get_profile":
            profile = context.profile_service.get_user_profile(user_id)
            item_ids = [item.id for item in (profile.profile.items if profile.profile else [])]
            state.profile_item_ids = item_ids
            state.add_refs(item_ids)
            return ToolExecutionResult(
                payload={
                    "hasProfile": profile.profile is not None,
                    "itemCount": len(item_ids),
                    "message": profile.message,
                },
                output_refs=item_ids,
            )

        if tool_name == "get_knowledge_graph":
            concept_id = params.get("conceptId", "concept_low_saturation")
            graph = context.knowledge_service.get_one_hop_graph(concept_id)
            if graph is None:
                return ToolExecutionResult(payload={"found": False}, output_refs=[])
            concept_ids = [concept.id for concept in graph.concepts]
            edge_ids = [edge.relation.id for edge in graph.edges]
            refs = [*concept_ids, *edge_ids]
            state.add_refs(refs)
            return ToolExecutionResult(
                payload={"rootConceptId": graph.root_concept_id, "conceptCount": len(graph.concepts)},
                output_refs=refs,
            )

        if tool_name == "list_knowledge_chunks":
            chunks = context.knowledge_service.list_chunks()
            doc_ids = [chunk.doc_id for chunk in chunks.chunks]
            state.add_refs(doc_ids)
            return ToolExecutionResult(
                payload={"total": chunks.total},
                output_refs=doc_ids,
            )

        if tool_name == "list_external_context":
            items = context.external_import_repository.list_confirmed_items(user_id)
            item_ids = [item.id for item in items]
            state.external_item_ids = item_ids
            state.add_refs(item_ids)
            return ToolExecutionResult(
                payload={"total": len(items), "titles": [item.title for item in items[:3]]},
                output_refs=item_ids,
            )

        raise ValueError(f"Unhandled tool: {tool_name}")


@dataclass
class PlannedToolCall:
    tool_name: str
    reason: str
    params: dict[str, Any]


class MockObservationPlanner:
    def plan_next(self, state: ObservationRunState) -> PlannedToolCall | None:
        if "list_reports" not in state.executed_tools:
            return PlannedToolCall(
                tool_name="list_reports",
                reason="先列出用户已有报告，确定可引用的观察证据。",
                params={},
            )
        if not state.report_ids:
            return None
        if "get_report" not in state.executed_tools and state.latest_report_id:
            return PlannedToolCall(
                tool_name="get_report",
                reason="读取最近一份报告详情，用于生成观察摘要。",
                params={"reportId": state.latest_report_id},
            )
        if "get_timeline_summary" not in state.executed_tools:
            return PlannedToolCall(
                tool_name="get_timeline_summary",
                reason="聚合时间轴摘要，补充跨报告的观察线索。",
                params={"period": state.period},
            )
        if "get_profile" not in state.executed_tools:
            return PlannedToolCall(
                tool_name="get_profile",
                reason="读取轻量画像条目，确认哪些倾向已有 feedback 证据。",
                params={},
            )
        if "list_external_context" not in state.executed_tools:
            return PlannedToolCall(
                tool_name="list_external_context",
                reason="检查用户已确认的外部补充上下文（如有）。",
                params={},
            )
        if "list_timeline_events" not in state.executed_tools:
            return PlannedToolCall(
                tool_name="list_timeline_events",
                reason="列出最近时间轴事件，便于绑定 evidence refs。",
                params={},
            )
        return None


MAX_TOOL_STEPS = 6


def build_observation_output(state: ObservationRunState) -> tuple[str | None, list[ObservationQuestion], str | None]:
    if not state.report_ids:
        return None, [], "还没有足够的报告记录，暂时无法生成观察摘要。完成更多分析后再试。"

    parts: list[str] = []
    if state.latest_report_title:
        parts.append(f"最近报告「{state.latest_report_title}」可作为当前观察起点。")
    if state.timeline_highlight_count:
        parts.append(f"时间轴在最近 {state.period} 内记录了 {state.timeline_highlight_count} 条可追溯变化。")
    if state.profile_item_ids:
        parts.append(f"轻量画像当前有 {len(state.profile_item_ids)} 条带来源 evidence 的倾向条目。")
    if state.external_item_ids:
        parts.append(f"另有 {len(state.external_item_ids)} 条已确认的外部补充上下文可供参考。")

    summary = " ".join(parts) if parts else "基于已有记录生成观察摘要。"
    summary += " 本摘要只聚合已有证据，不构成人格或心理判断。"

    questions: list[ObservationQuestion] = []
    if state.timeline_event_ids:
        questions.append(
            ObservationQuestion(
                text="最近时间轴事件里，哪些变化与你当前输入最相关？",
                evidenceRefs=state.timeline_event_ids[:2],
            )
        )
    if state.latest_report_id:
        questions.append(
            ObservationQuestion(
                text="最近一次报告中的哪些结构特征值得在下一次输入里继续观察？",
                evidenceRefs=[state.latest_report_id],
            )
        )

    return summary, questions[:3], None


def run_tool_step(
    *,
    registry: AgentToolRegistry,
    planner: MockObservationPlanner,
    context: ToolContext,
    state: ObservationRunState,
    step_index: int,
) -> tuple[PlannedToolCall | None, ToolExecutionResult | None, int]:
    planned = planner.plan_next(state)
    if planned is None:
        return None, None, 0

    started = perf_counter()
    result = registry.execute(planned.tool_name, state.user_id, planned.params, context, state)
    latency_ms = int((perf_counter() - started) * 1000)
    state.executed_tools.add(planned.tool_name)
    return planned, result, latency_ms
