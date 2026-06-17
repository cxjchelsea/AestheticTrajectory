import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { LoadingState } from "../components/LoadingState";
import { JobStatusPanel } from "../features/analysis/JobStatusPanel";
import { createAnalysisJob } from "../services/analysisJobApi";
import { createInput } from "../services/inputApi";
import { getReport } from "../services/reportApi";
import type { AestheticInput, ReportResponse } from "../types/aesthetic";

interface AnalysisRunResult {
  report: ReportResponse;
  jobId?: string;
  canPersistFeedback: boolean;
}

const analysisRunPromises = new Map<string, Promise<AnalysisRunResult>>();

interface AnalysisJobPageProps {
  runId: string;
  inputs: AestheticInput[];
  fallbackReport: ReportResponse;
  onComplete: (report: ReportResponse, jobId?: string, canPersistFeedback?: boolean) => void;
  onBack: () => void;
}

export function AnalysisJobPage({ runId, inputs, fallbackReport, onComplete, onBack }: AnalysisJobPageProps) {
  const [activeStep, setActiveStep] = useState(0);
  const [statusLabel, setStatusLabel] = useState("准备提交样本");
  const [fallbackReason, setFallbackReason] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function startAnalysis() {
      const existingRun = analysisRunPromises.get(runId);
      if (existingRun) {
        setStatusLabel("正在等待分析结果");
        return existingRun;
      }

      const nextRun = (async () => {
        setActiveStep(0);
        setStatusLabel("正在保存输入样本");
        const createdInputs = await Promise.all(
          inputs.map(({ id: _id, ...input }) => createInput(input))
        );

        setActiveStep(1);
        setStatusLabel("正在创建分析任务");
        const job = await createAnalysisJob(createdInputs.map((input) => input.id));

        setActiveStep(3);
        setStatusLabel("正在读取分析报告");
        if (!job.reportId) {
          throw new Error("Analysis job completed without reportId");
        }
        const report = await getReport(job.reportId);

        return {
          report,
          jobId: job.id,
          canPersistFeedback: true,
        };
      })();

      analysisRunPromises.set(runId, nextRun);
      return nextRun;
    }

    async function runAnalysis() {
      try {
        const result = await startAnalysis();
        if (cancelled) return;
        setActiveStep(4);
        setStatusLabel("分析完成");
        window.setTimeout(() => onComplete(result.report, result.jobId, result.canPersistFeedback), 350);
      } catch (error) {
        if (cancelled) return;
        setFallbackReason(error instanceof Error ? error.message : "API request failed");
        setActiveStep(4);
        setStatusLabel("后端不可用，已切换为本地 mock 报告");
        window.setTimeout(() => onComplete(fallbackReport, undefined, false), 700);
      }
    }

    runAnalysis();
    return () => {
      cancelled = true;
    };
  }, [fallbackReport, inputs, onComplete, runId]);

  return (
    <main className="page analysis-page">
      <button className="text-button" onClick={onBack}>返回上传</button>
      <h1>正在分析 {inputs.length} 个样本</h1>
      <p className="muted">优先调用 V1 后端 mock workflow；后端不可用时自动回退到本地 mock 报告。</p>
      <LoadingState label={statusLabel} />
      <JobStatusPanel activeStep={activeStep} />
      {fallbackReason ? <p className="muted">Fallback reason: {fallbackReason}</p> : null}
      <Button variant="secondary" onClick={() => onComplete(fallbackReport, undefined, false)}>使用本地 mock 报告</Button>
    </main>
  );
}
