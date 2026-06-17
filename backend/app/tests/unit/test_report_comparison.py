from app.schemas.report import ReportResponse
from app.services.report_comparison import build_latest_report_comparison


def test_report_comparison_returns_empty_state_for_insufficient_history() -> None:
    comparison = build_latest_report_comparison("user_a", [_report("report_1", "warm")])

    assert comparison.previous_report is None
    assert comparison.current_report is None
    assert comparison.feature_changes == []
    assert comparison.message == "历史报告不足两份，暂时无法生成最近变化说明。"


def test_report_comparison_builds_evidence_backed_changes_without_diagnosis() -> None:
    previous = _report("report_previous", "warm", interpretation_name="柔和秩序")
    current = _report("report_current", "contrast", interpretation_name="高对比张力")

    comparison = build_latest_report_comparison("user_a", [current, previous])

    assert comparison.previous_report is not None
    assert comparison.previous_report.report_id == "report_previous"
    assert comparison.current_report is not None
    assert comparison.current_report.report_id == "report_current"
    assert comparison.feature_changes
    assert any(change.change_type == "new" for change in comparison.feature_changes)
    assert all(change.evidence_refs for change in comparison.feature_changes)
    assert comparison.interpretation_changes
    assert comparison.summary is not None
    assert "人格" not in comparison.summary
    assert "心理" not in comparison.summary
    assert "能力" not in comparison.summary
    assert "report_current" in {
        evidence_ref for change in comparison.feature_changes for evidence_ref in change.evidence_refs
    }


def _report(report_id: str, mood_value: str, interpretation_name: str = "柔和秩序") -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
        title=f"{report_id} title",
        summary=f"{report_id} summary",
        lowLevelFeatures=[
            {
                "inputId": f"{report_id}_input_1",
                "featureType": "text",
                "lowLevelFeatures": {
                    "color_mood": {
                        "value": mood_value,
                        "confidence": 0.8,
                        "evidence": ["evidence_1"],
                    },
                    "composition": {
                        "value": "centered",
                        "confidence": 0.7,
                        "evidence": ["evidence_2"],
                    },
                },
                "sampleEvidence": ["sample evidence"],
                "promptVersion": "test",
                "modelName": "mock",
            }
        ],
        similarityGroups=[],
        possibleInterpretations=[
            {
                "id": f"{report_id}_interpretation",
                "name": interpretation_name,
                "confidence": 0.7,
                "evidenceRefs": [f"{report_id}_input_1"],
                "uncertainty": "测试样本有限",
            }
        ],
        insights=[
            {
                "insightId": f"{report_id}_insight",
                "title": interpretation_name,
                "observation": "观察到局部结构变化。",
                "evidenceRefs": [f"{report_id}_input_1"],
                "interpretation": "这是输入之间的结构差异。",
                "uncertainty": "仅用于测试。",
                "confidence": 0.7,
            }
        ],
        disclaimer="测试报告。",
    )
