import { EvidenceList } from "../../components/EvidenceList";
import type { AestheticInput, Insight } from "../../types/aesthetic";

interface InsightCardProps {
  insight: Insight;
  inputs: AestheticInput[];
}

export function InsightCard({ insight, inputs }: InsightCardProps) {
  return (
    <article className="insight-card">
      <div className="card-heading">
        <h3>{insight.title}</h3>
        <span>{Math.round(insight.confidence * 100)}%</span>
      </div>
      <p>{insight.observation}</p>
      <p>{insight.interpretation}</p>
      <small>{insight.uncertainty}</small>
      <EvidenceList evidenceRefs={insight.evidenceRefs} inputs={inputs} />
    </article>
  );
}
