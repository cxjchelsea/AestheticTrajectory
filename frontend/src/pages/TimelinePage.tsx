import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { getTimeline, getTimelineSummary } from "../services/timelineApi";
import type { TimelineListResponse, TimelineSummaryResponse } from "../types/aesthetic";

interface TimelinePageProps {
  userId: string;
  onBack: () => void;
  onStart: () => void;
  onViewHistory: () => void;
  onViewComparison: () => void;
}

export function TimelinePage({
  userId,
  onBack,
  onStart,
  onViewHistory,
  onViewComparison,
}: TimelinePageProps) {
  const [timeline, setTimeline] = useState<TimelineListResponse | null>(null);
  const [summary, setSummary] = useState<TimelineSummaryResponse | null>(null);
  const [period, setPeriod] = useState<"week" | "month">("month");
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadTimeline() {
      try {
        setStatus("loading");
        const [timelineResponse, summaryResponse] = await Promise.all([
          getTimeline(userId),
          getTimelineSummary(userId, period),
        ]);
        if (cancelled) return;
        setTimeline(timelineResponse);
        setSummary(summaryResponse);
        setStatus("ready");
      } catch (error) {
        if (cancelled) return;
        setErrorMessage(error instanceof Error ? error.message : "API request failed");
        setStatus("error");
      }
    }

    loadTimeline();
    return () => {
      cancelled = true;
    };
  }, [userId, period]);

  return (
    <main className="page timeline-page">
      <div className="report-header">
        <div>
          <p className="eyebrow">V4-B Timeline</p>
          <h1>审美时间轴</h1>
          <p className="lead">按时间汇总可追溯的报告、特征变化与反馈事件，不做人格或心理发展叙事。</p>
        </div>
        <div className="hero-actions">
          <Button variant="secondary" onClick={onBack}>返回首页</Button>
          <Button variant="secondary" onClick={onViewHistory}>历史报告</Button>
          <Button variant="secondary" onClick={onViewComparison}>最近变化</Button>
          <Button onClick={onStart}>开始一次分析</Button>
        </div>
      </div>

      <section className="comparison-section">
        <div className="hero-actions">
          <Button variant={period === "week" ? "primary" : "secondary"} onClick={() => setPeriod("week")}>最近一周</Button>
          <Button variant={period === "month" ? "primary" : "secondary"} onClick={() => setPeriod("month")}>最近一月</Button>
        </div>
      </section>

      {status === "loading" ? <p className="muted">正在读取审美时间轴...</p> : null}

      {status === "error" ? (
        <section className="empty-state">
          <h2>暂时无法读取时间轴</h2>
          <p>{errorMessage}</p>
          <Button variant="secondary" onClick={onBack}>返回首页</Button>
        </section>
      ) : null}

      {status === "ready" && summary ? (
        <section className="comparison-summary">
          <h2>周期观察摘要</h2>
          {summary.message ? <p>{summary.message}</p> : <p>{summary.summaryText}</p>}
          <p className="disclaimer">{summary.disclaimer}</p>
          {summary.highlights.length > 0 ? (
            <ul>
              {summary.highlights.map((item) => (
                <li key={`${item.eventType}-${item.title}-${item.occurredAt}`}>
                  {new Date(item.occurredAt).toLocaleString()} · {item.title}
                </li>
              ))}
            </ul>
          ) : null}
        </section>
      ) : null}

      {status === "ready" && timeline?.message && timeline.events.length === 0 ? (
        <section className="empty-state">
          <h2>还没有时间轴事件</h2>
          <p>{timeline.message}</p>
          <Button onClick={onStart}>开始一次分析</Button>
        </section>
      ) : null}

      {status === "ready" && timeline && timeline.events.length > 0 ? (
        <section className="history-list" aria-label="审美时间轴事件列表">
          {timeline.events.map((event) => (
            <article className="history-card" key={event.id}>
              <div>
                <p className="eyebrow">{new Date(event.occurredAt).toLocaleString()} · {event.eventType}</p>
                <h2>{event.title}</h2>
                {event.description ? <p>{event.description}</p> : null}
                <small>
                  证据：{event.evidence.evidenceRefs.join(" · ")}
                  {event.relatedReportIds.length > 0 ? ` · 报告 ${event.relatedReportIds.join(", ")}` : ""}
                </small>
              </div>
            </article>
          ))}
        </section>
      ) : null}
    </main>
  );
}
