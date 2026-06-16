import { Button } from "../components/Button";
import { FeedbackPanel } from "../features/report/FeedbackPanel";
import { InsightCard } from "../features/report/InsightCard";
import { ReportSection } from "../features/report/ReportSection";
import { starterInputs } from "../services/mockData";
import type { AestheticInput, ReportResponse } from "../types/aesthetic";

interface ReportDetailPageProps {
  report: ReportResponse;
  inputs: AestheticInput[];
  onRestart: () => void;
  onViewHistory: () => void;
}

export function ReportDetailPage({ report, inputs, onRestart, onViewHistory }: ReportDetailPageProps) {
  const evidenceInputs = inputs.length >= 3 ? inputs : starterInputs;

  return (
    <main className="page report-page">
      <div className="report-header">
        <div>
          <p className="eyebrow">Mock Report</p>
          <h1>{report.title}</h1>
          <p>{report.summary}</p>
        </div>
        <div className="hero-actions">
          <Button variant="secondary" onClick={onViewHistory}>历史报告</Button>
          <Button variant="secondary" onClick={onRestart}>重新上传</Button>
        </div>
      </div>

      <ReportSection title="底层特征摘要">
        <div className="feature-grid">
          {report.lowLevelFeatures.map((feature) => (
            <article className="feature-card" key={feature.inputId}>
              <h3>{feature.inputId}</h3>
              {Object.entries(feature.lowLevelFeatures).map(([name, signal]) => (
                <p key={name}>
                  <strong>{name}</strong>
                  <span>{signal.value} · {Math.round(signal.confidence * 100)}%</span>
                </p>
              ))}
            </article>
          ))}
        </div>
      </ReportSection>

      <ReportSection title="相似性分组">
        {report.similarityGroups.map((group) => (
          <article className="wide-item" key={group.groupId}>
            <h3>{group.name}</h3>
            <p>{group.commonFeatures.join(" / ")}</p>
            <small>{group.uncertainty}</small>
          </article>
        ))}
      </ReportSection>

      <ReportSection title="可能解释">
        <div className="interpretation-list">
          {report.possibleInterpretations.map((item) => (
            <article className="wide-item" key={item.id}>
              <h3>{item.name}</h3>
              <p>置信度 {Math.round(item.confidence * 100)}%</p>
              <small>{item.uncertainty}</small>
            </article>
          ))}
        </div>
      </ReportSection>

      <ReportSection title="重点洞察">
        {report.insights.map((insight) => (
          <div key={insight.insightId} className="insight-block">
            <InsightCard insight={insight} inputs={evidenceInputs} />
            <FeedbackPanel insightId={insight.insightId} />
          </div>
        ))}
      </ReportSection>

      <p className="disclaimer">{report.disclaimer}</p>
    </main>
  );
}
