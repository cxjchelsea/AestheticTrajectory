import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { FeedbackPanel } from "../features/report/FeedbackPanel";
import { InsightCard } from "../features/report/InsightCard";
import { ReportSection } from "../features/report/ReportSection";
import { getAnalysisJobDebug } from "../services/analysisJobApi";
import { getReportEvaluation } from "../services/reportApi";
import { starterInputs } from "../services/mockData";
import type { AestheticInput, AnalysisJobDebugResponse, ReportEvaluationResponse, ReportResponse } from "../types/aesthetic";

interface ReportDetailPageProps {
  report: ReportResponse;
  inputs: AestheticInput[];
  debugJobId?: string | null;
  canPersistFeedback?: boolean;
  onHome: () => void;
  onRestart: () => void;
  onViewHistory: () => void;
  onViewProfile: () => void;
}

export function ReportDetailPage({
  report,
  inputs,
  debugJobId,
  canPersistFeedback = true,
  onHome,
  onRestart,
  onViewHistory,
  onViewProfile
}: ReportDetailPageProps) {
  const evidenceInputs = inputs.length >= 3 ? inputs : starterInputs;
  const [debugPayload, setDebugPayload] = useState<AnalysisJobDebugResponse | null>(null);
  const [debugError, setDebugError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<ReportEvaluationResponse | null>(null);
  const [evaluationRefreshKey, setEvaluationRefreshKey] = useState(0);

  useEffect(() => {
    if (!canPersistFeedback) {
      setEvaluation(null);
      return;
    }

    let cancelled = false;
    async function loadEvaluation() {
      try {
        const payload = await getReportEvaluation(report.reportId);
        if (cancelled) return;
        setEvaluation(payload);
      } catch {
        if (cancelled) return;
        setEvaluation(null);
      }
    }

    loadEvaluation();
    return () => {
      cancelled = true;
    };
  }, [canPersistFeedback, report.reportId, evaluationRefreshKey]);

  useEffect(() => {
    if (!import.meta.env.DEV || !debugJobId) {
      setDebugPayload(null);
      setDebugError(null);
      return;
    }

    let cancelled = false;
    async function loadDebugPayload() {
      try {
        const payload = await getAnalysisJobDebug(debugJobId as string);
        if (cancelled) return;
        setDebugPayload(payload);
        setDebugError(null);
      } catch (error) {
        if (cancelled) return;
        setDebugPayload(null);
        setDebugError(error instanceof Error ? error.message : "Debug payload request failed");
      }
    }

    loadDebugPayload();
    return () => {
      cancelled = true;
    };
  }, [debugJobId]);

  return (
    <main className="page report-page">
      <div className="report-header">
        <div>
          <p className="eyebrow">Mock Report</p>
          <h1>{report.title}</h1>
          <p>{report.summary}</p>
        </div>
        <div className="hero-actions">
          <Button variant="secondary" onClick={onHome}>返回首页</Button>
          <Button variant="secondary" onClick={onViewHistory}>历史报告</Button>
          <Button variant="secondary" onClick={onViewProfile}>轻量画像</Button>
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

      {report.historyContext ? (
        <ReportSection title="历史参考">
          {report.historyContext.summary ? <p>{report.historyContext.summary}</p> : null}
          {report.historyContext.message && report.historyContext.items.length === 0 ? (
            <p className="muted">{report.historyContext.message}</p>
          ) : null}
          <div className="history-context-list">
            {report.historyContext.items.map((item) => (
              <article className="wide-item" key={`${item.sourceType}-${item.sourceId}-${item.direction}`}>
                <h3>{item.label}</h3>
                <p>{item.note}</p>
                <small>
                  {item.sourceType} · {item.direction}
                  {item.matchedFeatures.length > 0 ? ` · ${item.matchedFeatures.join(" / ")}` : ""}
                </small>
                <small>来源：{item.sourceRefs.join(", ")}</small>
              </article>
            ))}
          </div>
          <p className="disclaimer">{report.historyContext.disclaimer}</p>
        </ReportSection>
      ) : null}

      {report.knowledgeContext ? (
        <ReportSection title="知识参考">
          {report.knowledgeContext.summary ? <p>{report.knowledgeContext.summary}</p> : null}
          {report.knowledgeContext.message && report.knowledgeContext.items.length === 0 ? (
            <p className="muted">{report.knowledgeContext.message}</p>
          ) : null}
          <div className="history-context-list">
            {report.knowledgeContext.items.map((item) => (
              <article className="wide-item" key={item.docId}>
                <h3>{item.title}</h3>
                <p>{item.snippet}</p>
                <p>{item.note}</p>
                {item.relationNotes && item.relationNotes.length > 0 ? (
                  <ul className="relation-notes">
                    {item.relationNotes.map((note) => (
                      <li key={note}>{note}</li>
                    ))}
                  </ul>
                ) : null}
                {item.relatedConceptIds && item.relatedConceptIds.length > 0 ? (
                  <small>相关概念：{item.relatedConceptIds.join(", ")}</small>
                ) : null}
                <small>
                  {item.matchedFeatures.length > 0 ? item.matchedFeatures.join(" / ") : "无特征匹配"}
                </small>
                <small>来源：{item.sourceRefs.join(", ")}</small>
              </article>
            ))}
          </div>
          <p className="disclaimer">{report.knowledgeContext.disclaimer}</p>
        </ReportSection>
      ) : null}

      {evaluation || report.evaluationMetrics ? (
        <ReportSection title="质量评估">
          <p>{evaluation?.summary ?? "当前报告已记录生成时的基础质量指标。"}</p>
          <div className="feature-grid">
            <article className="feature-card">
              <h3>Evidence Coverage</h3>
              <p>{formatRate(evaluation?.metrics.evidenceCoverage ?? report.evaluationMetrics?.evidenceCoverage)}</p>
            </article>
            <article className="feature-card">
              <h3>Retrieval Coverage</h3>
              <p>{formatRate(evaluation?.metrics.retrievalCoverage ?? report.evaluationMetrics?.retrievalCoverage)}</p>
            </article>
            <article className="feature-card">
              <h3>Unsupported Insights</h3>
              <p>{evaluation?.metrics.unsupportedInsightCount ?? report.evaluationMetrics?.unsupportedInsightCount ?? 0}</p>
            </article>
            <article className="feature-card">
              <h3>Schema Pass Rate</h3>
              <p>{formatRate(evaluation?.metrics.schemaPassRate ?? report.evaluationMetrics?.schemaPassRate)}</p>
            </article>
            <article className="feature-card">
              <h3>Feedback Hit Rate</h3>
              <p>{formatOptionalRate(evaluation?.metrics.feedbackHitRate ?? report.evaluationMetrics?.feedbackHitRate)}</p>
            </article>
          </div>
          <p className="disclaimer">{evaluation?.disclaimer ?? "这些指标用于开发期质量观察，不代表对用户的人格、心理或能力判断。"}</p>
        </ReportSection>
      ) : null}

      <ReportSection title="重点洞察">
        {report.insights.map((insight) => (
          <div key={insight.insightId} className="insight-block">
            <InsightCard insight={insight} inputs={evidenceInputs} />
            <FeedbackPanel
              insightId={insight.insightId}
              canPersist={canPersistFeedback}
              onFeedbackSaved={() => setEvaluationRefreshKey((value) => value + 1)}
            />
          </div>
        ))}
      </ReportSection>

      {import.meta.env.DEV && debugJobId ? (
        <DeveloperDebugPanel debug={debugPayload} errorMessage={debugError} />
      ) : null}

      <p className="disclaimer">{report.disclaimer}</p>
    </main>
  );
}

function formatRate(value: number | null | undefined) {
  if (value === null || value === undefined) return "—";
  return `${Math.round(value * 100)}%`;
}

function formatOptionalRate(value: number | null | undefined) {
  if (value === null || value === undefined) return "尚无反馈";
  return `${Math.round(value * 100)}%`;
}

function DeveloperDebugPanel({
  debug,
  errorMessage
}: {
  debug: AnalysisJobDebugResponse | null;
  errorMessage: string | null;
}) {
  return (
    <details className="debug-panel">
      <summary>Developer Debug</summary>
      {errorMessage ? <p className="debug-warning">Debug payload unavailable: {errorMessage}</p> : null}
      {!debug && !errorMessage ? <p className="muted">正在读取 workflow debug trace...</p> : null}
      {debug ? (
        <div className="debug-grid">
          <section>
            <h3>Workflow Trace</h3>
            <ul>
              {debug.workflowTrace.map((step) => (
                <li key={step.id}>
                  <strong>{step.stepId}</strong>
                  <span>{step.status}</span>
                  <small>{step.latencyMs ?? 0}ms</small>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3>Fallback Events</h3>
            {debug.fallbackEvents.length > 0 ? (
              <ul>
                {debug.fallbackEvents.map((event) => (
                  <li key={event.id}>
                    <strong>{event.fallbackType}</strong>
                    <span>{event.fallbackAction}</span>
                    <small>{event.developerMessage}</small>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">暂无显性降级事件。</p>
            )}
          </section>

          <section>
            <h3>Mock Usage</h3>
            <ul>
              {debug.mockUsage.map((item) => (
                <li key={item.component}>
                  <strong>{item.component}</strong>
                  <span>{item.status}{item.devOnly ? " · dev-only" : ""}</span>
                  <small>{item.developerMessage}</small>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3>Schema Validation</h3>
            <ul>
              {debug.schemaValidation.map((item) => (
                <li key={`${item.stepId}-${item.schemaName}`}>
                  <strong>{item.schemaName}</strong>
                  <span>{item.status}</span>
                  <small>{item.developerMessage}</small>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3>Boundary Warnings</h3>
            <ul>
              {debug.boundaryWarnings.map((warning) => (
                <li key={warning.capability}>
                  <strong>{warning.capability}</strong>
                  <span>{warning.status}</span>
                  <small>{warning.developerMessage}</small>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3>Retrieval Trace</h3>
            {debug.retrievalTrace.length > 0 ? (
              <ul>
                {debug.retrievalTrace.map((step) => (
                  <li key={step.stepId}>
                    <strong>{step.retrievalType}</strong>
                    <span>{step.status}</span>
                    <span>{step.selectedItemCount} selected</span>
                    {step.abstained ? <span>abstained</span> : null}
                    {step.graphHitCount != null ? <span>graph {step.graphHitCount}</span> : null}
                    {step.vectorPath ? <span>vector {step.vectorPath}</span> : null}
                    <small>{step.developerMessage}</small>
                    {step.message ? <small>{step.message}</small> : null}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">暂无 retrieval trace。</p>
            )}
          </section>

          <section>
            <h3>Retrieval Items</h3>
            {debug.retrievalItems.length > 0 ? (
              <ul>
                {debug.retrievalItems.map((item) => (
                  <li key={`${item.retrievalType}-${item.itemId}`}>
                    <strong>{item.label}</strong>
                    <span>{item.retrievalType}</span>
                    <small>{item.matchedFeatures.join(" · ")}</small>
                    <small>{item.sourceRefs.join(" · ")}</small>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">暂无选中 retrieval item。</p>
            )}
          </section>

          <section>
            <h3>Context Assembly</h3>
            {debug.contextAssemblyTrace ? (
              <div>
                <p>
                  history {debug.contextAssemblyTrace.historyItemCount} · knowledge{" "}
                  {debug.contextAssemblyTrace.knowledgeItemCount}
                </p>
                <small>{debug.contextAssemblyTrace.developerMessage}</small>
                {debug.contextAssemblyTrace.historyMessage ? (
                  <small>{debug.contextAssemblyTrace.historyMessage}</small>
                ) : null}
                {debug.contextAssemblyTrace.knowledgeMessage ? (
                  <small>{debug.contextAssemblyTrace.knowledgeMessage}</small>
                ) : null}
              </div>
            ) : (
              <p className="muted">暂无 context assembly trace。</p>
            )}
          </section>

          <section>
            <h3>Evaluation Trace</h3>
            {debug.evaluationTrace ? (
              <div>
                <p>
                  evidence {formatRate(debug.evaluationTrace.metrics.evidenceCoverage)} · retrieval{" "}
                  {formatRate(debug.evaluationTrace.metrics.retrievalCoverage)} · unsupported{" "}
                  {debug.evaluationTrace.metrics.unsupportedInsightCount}
                </p>
                <small>{debug.evaluationTrace.developerMessage}</small>
              </div>
            ) : (
              <p className="muted">暂无 evaluation trace。</p>
            )}
          </section>
        </div>
      ) : null}
    </details>
  );
}
