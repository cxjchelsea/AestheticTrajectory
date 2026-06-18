import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { getReport, getReportHistory } from "../services/reportApi";
import type { ReportHistoryResponse, ReportResponse } from "../types/aesthetic";

interface HistoryPageProps {
  userId: string;
  onOpenReport: (report: ReportResponse, jobId?: string | null) => void;
  onStart: () => void;
  onViewProfile: () => void;
  onViewComparison: () => void;
  onViewTimeline: () => void;
  onBack: () => void;
}

export function HistoryPage({
  userId,
  onOpenReport,
  onStart,
  onViewProfile,
  onViewComparison,
  onViewTimeline,
  onBack,
}: HistoryPageProps) {
  const [history, setHistory] = useState<ReportHistoryResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [openingReportId, setOpeningReportId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      try {
        setStatus("loading");
        const response = await getReportHistory(userId);
        if (cancelled) return;
        setHistory(response);
        setStatus("ready");
      } catch (error) {
        if (cancelled) return;
        setErrorMessage(error instanceof Error ? error.message : "API request failed");
        setStatus("error");
      }
    }

    loadHistory();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  async function openReport(reportId: string, jobId?: string | null) {
    try {
      setOpeningReportId(reportId);
      const report = await getReport(reportId);
      onOpenReport(report, jobId);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "API request failed");
      setStatus("error");
    } finally {
      setOpeningReportId(null);
    }
  }

  return (
    <main className="page history-page">
      <div className="report-header">
        <div>
          <p className="eyebrow">V2-A History</p>
          <h1>历史报告</h1>
          <p className="lead">回看你已经生成过的审美观察报告。当前只做报告回看，不做画像或趋势判断。</p>
        </div>
        <div className="hero-actions">
          <Button variant="secondary" onClick={onBack}>返回首页</Button>
          <Button variant="secondary" onClick={onViewProfile}>查看轻量画像</Button>
          <Button variant="secondary" onClick={onViewComparison}>查看最近变化</Button>
          <Button variant="secondary" onClick={onViewTimeline}>查看审美时间轴</Button>
          <Button onClick={onStart}>开始一次分析</Button>
        </div>
      </div>

      {status === "loading" ? <p className="muted">正在读取历史报告...</p> : null}

      {status === "error" ? (
        <section className="empty-state">
          <h2>暂时无法读取历史报告</h2>
          <p>{errorMessage}</p>
          <Button variant="secondary" onClick={onBack}>返回首页</Button>
        </section>
      ) : null}

      {status === "ready" && history?.reports.length === 0 ? (
        <section className="empty-state">
          <h2>还没有历史报告</h2>
          <p>完成一次审美分析后，这里会保存你的报告，方便之后回看。</p>
          <Button onClick={onStart}>开始一次分析</Button>
        </section>
      ) : null}

      {status === "ready" && history && history.reports.length > 0 ? (
        <section className="history-list" aria-label="历史报告列表">
          {history.reports.map((report) => (
            <article className="history-card" key={report.reportId}>
              <div>
                <p className="eyebrow">{new Date(report.createdAt).toLocaleString()}</p>
                <h2>{report.title}</h2>
                <p>{report.summary}</p>
                <small>{report.inputCount} 个样本 · {report.jobId ?? "无任务 ID"}</small>
              </div>
              <Button
                variant="secondary"
                onClick={() => openReport(report.reportId, report.jobId)}
                disabled={openingReportId === report.reportId}
              >
                {openingReportId === report.reportId ? "打开中..." : "查看详情"}
              </Button>
            </article>
          ))}
        </section>
      ) : null}
    </main>
  );
}
