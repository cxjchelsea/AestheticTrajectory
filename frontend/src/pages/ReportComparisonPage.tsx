import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { getLatestReportComparison } from "../services/reportApi";
import type { ReportChangeType, ReportComparisonResponse } from "../types/aesthetic";

interface ReportComparisonPageProps {
  userId: string;
  onBack: () => void;
  onStart: () => void;
  onViewHistory: () => void;
  onViewTimeline?: () => void;
}

export function ReportComparisonPage({ userId, onBack, onStart, onViewHistory, onViewTimeline }: ReportComparisonPageProps) {
  const [comparison, setComparison] = useState<ReportComparisonResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadComparison() {
      try {
        setStatus("loading");
        const response = await getLatestReportComparison(userId);
        if (cancelled) return;
        setComparison(response);
        setStatus("ready");
      } catch (error) {
        if (cancelled) return;
        setErrorMessage(error instanceof Error ? error.message : "API request failed");
        setStatus("error");
      }
    }

    loadComparison();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  return (
    <main className="page comparison-page">
      <div className="report-header">
        <div>
          <p className="eyebrow">V2-D Recent Change</p>
          <h1>最近变化</h1>
          <p className="lead">对比最近两次报告中出现的输入特征和解释方向变化，不做长期趋势或人格判断。</p>
        </div>
        <div className="hero-actions">
          <Button variant="secondary" onClick={onBack}>返回首页</Button>
          <Button variant="secondary" onClick={onViewHistory}>查看历史报告</Button>
          {onViewTimeline ? <Button variant="secondary" onClick={onViewTimeline}>审美时间轴</Button> : null}
          <Button onClick={onStart}>开始一次分析</Button>
        </div>
      </div>

      {status === "loading" ? <p className="muted">正在读取最近变化...</p> : null}

      {status === "error" ? (
        <section className="empty-state">
          <h2>暂时无法读取最近变化</h2>
          <p>{errorMessage}</p>
          <Button variant="secondary" onClick={onViewHistory}>返回历史报告</Button>
        </section>
      ) : null}

      {status === "ready" && comparison?.message ? (
        <section className="empty-state">
          <h2>历史报告还不够</h2>
          <p>{comparison.message}</p>
          <p className="disclaimer">{comparison.disclaimer}</p>
          <Button onClick={onStart}>开始一次分析</Button>
        </section>
      ) : null}

      {status === "ready" && comparison && !comparison.message ? (
        <>
          <section className="comparison-summary">
            <div>
              <p className="eyebrow">上一份报告</p>
              <h2>{comparison.previousReport?.title}</h2>
              <p>{comparison.previousReport?.summary}</p>
            </div>
            <div>
              <p className="eyebrow">当前报告</p>
              <h2>{comparison.currentReport?.title}</h2>
              <p>{comparison.currentReport?.summary}</p>
            </div>
          </section>

          <section className="profile-summary">
            <p className="eyebrow">变化摘要</p>
            <h2>{comparison.summary}</h2>
            <p className="disclaimer">{comparison.disclaimer}</p>
          </section>

          <section className="comparison-section">
            <div className="section-heading">
              <h2>底层特征变化</h2>
              <p className="muted">基于最近两份 report_json 的 feature key/value 变化。</p>
            </div>
            <div className="comparison-list">
              {comparison.featureChanges.map((change) => (
                <article className="wide-item" key={`${change.changeType}-${change.label}`}>
                  <div className="card-heading">
                    <strong>{humanizeFeatureLabel(change.label)}</strong>
                    <span>{changeTypeLabel(change.changeType)}</span>
                  </div>
                  <p>{change.note}</p>
                  <small>
                    上一次 {change.previousCount} 次 · 这一次 {change.currentCount} 次 · 证据 {change.evidenceRefs.join(" / ")}
                  </small>
                </article>
              ))}
            </div>
          </section>

          <section className="comparison-section">
            <div className="section-heading">
              <h2>解释方向变化</h2>
              <p className="muted">只描述报告解释或洞察方向是否新增、延续或减弱。</p>
            </div>
            <div className="comparison-list">
              {comparison.interpretationChanges.map((change) => (
                <article className="wide-item" key={`${change.changeType}-${change.label}`}>
                  <div className="card-heading">
                    <strong>{change.label}</strong>
                    <span>{changeTypeLabel(change.changeType)}</span>
                  </div>
                  <p>{change.note}</p>
                  <small>证据 {change.evidenceRefs.join(" / ")}</small>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}

function changeTypeLabel(changeType: ReportChangeType) {
  const labels: Record<ReportChangeType, string> = {
    new: "新增",
    increased: "增强",
    decreased: "减弱",
    repeated: "重复出现",
  };
  return labels[changeType];
}

function humanizeFeatureLabel(label: string) {
  return label
    .replace("=", "：")
    .replaceAll("_", " ");
}
