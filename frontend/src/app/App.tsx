import { useMemo, useState } from "react";
import { HomePage } from "../pages/HomePage";
import { UploadPage } from "../pages/UploadPage";
import { AnalysisJobPage } from "../pages/AnalysisJobPage";
import { ReportDetailPage } from "../pages/ReportDetailPage";
import { HistoryPage } from "../pages/HistoryPage";
import { mockReport } from "../services/mockData";
import type { AestheticInput, AppRoute, ReportResponse } from "../types/aesthetic";

const CURRENT_USER_ID = "user_anonymous";

export function App() {
  const [route, setRoute] = useState<AppRoute>("home");
  const [inputs, setInputs] = useState<AestheticInput[]>([]);
  const [apiReport, setApiReport] = useState<ReportResponse | null>(null);

  const fallbackReport = useMemo(() => mockReport(inputs), [inputs]);
  const report = apiReport ?? fallbackReport;

  function startUploadFlow() {
    setApiReport(null);
    setRoute("upload");
  }

  if (route === "upload") {
    return <UploadPage inputs={inputs} onChange={setInputs} onStart={() => setRoute("analysis")} onBack={() => setRoute("home")} />;
  }

  if (route === "analysis") {
    return (
      <AnalysisJobPage
        inputs={inputs}
        fallbackReport={fallbackReport}
        onComplete={(nextReport) => {
          setApiReport(nextReport);
          setRoute("report");
        }}
        onBack={() => setRoute("upload")}
      />
    );
  }

  if (route === "report") {
    return (
      <ReportDetailPage
        report={report}
        inputs={inputs}
        onRestart={startUploadFlow}
        onViewHistory={() => setRoute("history")}
      />
    );
  }

  if (route === "history") {
    return (
      <HistoryPage
        userId={CURRENT_USER_ID}
        onOpenReport={(nextReport) => {
          setApiReport(nextReport);
          setInputs([]);
          setRoute("report");
        }}
        onStart={startUploadFlow}
        onBack={() => setRoute("home")}
      />
    );
  }

  return (
    <HomePage
      onStart={startUploadFlow}
      onViewDemo={() => setRoute("report")}
      onViewHistory={() => setRoute("history")}
    />
  );
}
