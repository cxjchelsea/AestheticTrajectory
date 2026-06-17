import { useMemo, useState } from "react";
import { HomePage } from "../pages/HomePage";
import { UploadPage } from "../pages/UploadPage";
import { AnalysisJobPage } from "../pages/AnalysisJobPage";
import { ReportDetailPage } from "../pages/ReportDetailPage";
import { HistoryPage } from "../pages/HistoryPage";
import { ProfilePage } from "../pages/ProfilePage";
import { mockReport } from "../services/mockData";
import type { AestheticInput, AppRoute, ReportResponse } from "../types/aesthetic";

const CURRENT_USER_ID = "user_anonymous";

export function App() {
  const [route, setRoute] = useState<AppRoute>("home");
  const [inputs, setInputs] = useState<AestheticInput[]>([]);
  const [apiReport, setApiReport] = useState<ReportResponse | null>(null);
  const [debugJobId, setDebugJobId] = useState<string | null>(null);
  const [canPersistFeedback, setCanPersistFeedback] = useState(false);
  const [analysisRunId, setAnalysisRunId] = useState("analysis_initial");

  const fallbackReport = useMemo(() => mockReport(inputs), [inputs]);
  const report = apiReport ?? fallbackReport;

  function startUploadFlow() {
    setApiReport(null);
    setDebugJobId(null);
    setCanPersistFeedback(false);
    setRoute("upload");
  }

  if (route === "upload") {
    return (
      <UploadPage
        inputs={inputs}
        onChange={setInputs}
        onStart={() => {
          setAnalysisRunId(`analysis_${Date.now()}`);
          setRoute("analysis");
        }}
        onBack={() => setRoute("home")}
      />
    );
  }

  if (route === "analysis") {
    return (
      <AnalysisJobPage
        runId={analysisRunId}
        inputs={inputs}
        fallbackReport={fallbackReport}
        onComplete={(nextReport, jobId, nextCanPersistFeedback) => {
          setApiReport(nextReport);
          setDebugJobId(jobId ?? null);
          setCanPersistFeedback(Boolean(nextCanPersistFeedback));
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
        debugJobId={debugJobId}
        canPersistFeedback={canPersistFeedback}
        onHome={() => setRoute("home")}
        onRestart={startUploadFlow}
        onViewHistory={() => setRoute("history")}
        onViewProfile={() => setRoute("profile")}
      />
    );
  }

  if (route === "history") {
    return (
      <HistoryPage
        userId={CURRENT_USER_ID}
        onOpenReport={(nextReport, jobId) => {
          setApiReport(nextReport);
          setDebugJobId(jobId ?? null);
          setCanPersistFeedback(true);
          setInputs([]);
          setRoute("report");
        }}
        onStart={startUploadFlow}
        onViewProfile={() => setRoute("profile")}
        onBack={() => setRoute("home")}
      />
    );
  }

  if (route === "profile") {
    return (
      <ProfilePage
        userId={CURRENT_USER_ID}
        onBack={() => setRoute("home")}
        onStart={startUploadFlow}
        onViewHistory={() => setRoute("history")}
      />
    );
  }

  return (
    <HomePage
      onStart={startUploadFlow}
      onViewDemo={() => {
        setApiReport(null);
        setDebugJobId(null);
        setCanPersistFeedback(false);
        setRoute("report");
      }}
      onViewHistory={() => setRoute("history")}
      onViewProfile={() => setRoute("profile")}
    />
  );
}
