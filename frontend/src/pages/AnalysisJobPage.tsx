import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { LoadingState } from "../components/LoadingState";
import { JobStatusPanel } from "../features/analysis/JobStatusPanel";
import { createAnalysisJob } from "../services/analysisJobApi";
import { createInput } from "../services/inputApi";
import { getReport } from "../services/reportApi";
import type { AestheticInput, ReportResponse } from "../types/aesthetic";

interface AnalysisJobPageProps {
  inputs: AestheticInput[];
  fallbackReport: ReportResponse;
  onComplete: (report: ReportResponse, jobId?: string) => void;
  onBack: () => void;
}

export function AnalysisJobPage({ inputs, fallbackReport, onComplete, onBack }: AnalysisJobPageProps) {
  const [activeStep, setActiveStep] = useState(0);
  const [statusLabel, setStatusLabel] = useState("准备提交样本");
  const [fallbackReason, setFallbackReason] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function runAnalysis() {
      try {
        setActiveStep(0);
        setStatusLabel("正在保存输入样本");
        const createdInputs = await Promise.all(
          inputs.map(({ id: _id, ...input }) => createInput(input))
        );

        if (cancelled) return;
        setActiveStep(1);
        setStatusLabel("正在创建分析任务");
        const job = await createAnalysisJob(createdInputs.map((input) => input.id));

        if (cancelled) return;
        setActiveStep(3);
        setStatusLabel("正在读取分析报告");
        if (!job.reportId) {
          throw new Error("Analysis job completed without reportId");
        }
        const report = await getReport(job.reportId);

        if (cancelled) return;
        setActiveStep(4);
        setStatusLabel("分析完成");
        window.setTimeout(() => onComplete(report, job.id), 350);
      } catch (error) {
        if (cancelled) return;
        setFallbackReason(error instanceof Error ? error.message : "API request failed");
        setActiveStep(4);
        setStatusLabel("后端不可用，已切换为本地 mock 报告");
        window.setTimeout(() => onComplete(fallbackReport), 700);
      }
    }

    runAnalysis();
    return () => {
      cancelled = true;
    };
  }, [fallbackReport, inputs, onComplete]);

  return (
    <main className="page analysis-page">
      <button className="text-button" onClick={onBack}>返回上传</button>
      <h1>正在分析 {inputs.length} 个样本</h1>
      <p className="muted">优先调用 V1 后端 mock workflow；后端不可用时自动回退到本地 mock 报告。</p>
      <LoadingState label={statusLabel} />
      <JobStatusPanel activeStep={activeStep} />
      {fallbackReason ? <p className="muted">Fallback reason: {fallbackReason}</p> : null}
      <Button variant="secondary" onClick={() => onComplete(fallbackReport)}>使用本地 mock 报告</Button>
    </main>
  );
}
