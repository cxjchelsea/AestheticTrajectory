import { useEffect, useMemo, useState } from "react";
import { HomePage } from "../pages/HomePage";
import { UploadPage } from "../pages/UploadPage";
import { AnalysisJobPage } from "../pages/AnalysisJobPage";
import { ReportDetailPage } from "../pages/ReportDetailPage";
import { HistoryPage } from "../pages/HistoryPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ReportComparisonPage } from "../pages/ReportComparisonPage";
import { TimelinePage } from "../pages/TimelinePage";
import { mockReport } from "../services/mockData";
import { bootstrapSession } from "../services/sessionApi";
import type { AestheticInput, AppRoute, ReportResponse } from "../types/aesthetic";
import { SessionContext } from "./sessionContext";

const DEV_USER_ID = "user_anonymous";

export function App() {
  const [route, setRoute] = useState<AppRoute>("home");
  const [inputs, setInputs] = useState<AestheticInput[]>([]);
  const [apiReport, setApiReport] = useState<ReportResponse | null>(null);
  const [debugJobId, setDebugJobId] = useState<string | null>(null);
  const [canPersistFeedback, setCanPersistFeedback] = useState(false);
  const [analysisRunId, setAnalysisRunId] = useState("analysis_initial");
  const [userId, setUserId] = useState(DEV_USER_ID);
  const [authMode, setAuthMode] = useState("dev");
  const [sessionReady, setSessionReady] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function initSession() {
      try {
        const session = await bootstrapSession();
        if (!cancelled) {
          setUserId(session.userId);
          setAuthMode(session.authMode);
        }
      } catch {
        if (!cancelled) {
          setUserId(DEV_USER_ID);
          setAuthMode("dev");
        }
      } finally {
        if (!cancelled) {
          setSessionReady(true);
        }
      }
    }

    void initSession();
    return () => {
      cancelled = true;
    };
  }, []);

  const sessionValue = useMemo(
    () => ({
      userId,
      authMode,
      sessionReady
    }),
    [authMode, sessionReady, userId]
  );

  const fallbackReport = useMemo(() => mockReport(inputs), [inputs]);
  const report = apiReport ?? fallbackReport;

  function startUploadFlow() {
    setApiReport(null);
    setDebugJobId(null);
    setCanPersistFeedback(false);
    setRoute("upload");
  }

  if (!sessionReady) {
    return <div className="page-shell">正在初始化会话…</div>;
  }

  const appBody = (() => {
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
          onComplete={(nextReport, jobId, nextCanPersistFeedback, createdInputs) => {
            setApiReport(nextReport);
            setDebugJobId(jobId ?? null);
            setCanPersistFeedback(Boolean(nextCanPersistFeedback));
            if (createdInputs?.length) {
              setInputs(createdInputs);
            }
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
          userId={userId}
          onOpenReport={(nextReport, jobId) => {
            setApiReport(nextReport);
            setDebugJobId(jobId ?? null);
            setCanPersistFeedback(true);
            setInputs([]);
            setRoute("report");
          }}
          onStart={startUploadFlow}
          onViewProfile={() => setRoute("profile")}
          onViewComparison={() => setRoute("comparison")}
          onViewTimeline={() => setRoute("timeline")}
          onBack={() => setRoute("home")}
        />
      );
    }

    if (route === "comparison") {
      return (
        <ReportComparisonPage
          userId={userId}
          onBack={() => setRoute("home")}
          onStart={startUploadFlow}
          onViewHistory={() => setRoute("history")}
          onViewTimeline={() => setRoute("timeline")}
        />
      );
    }

    if (route === "timeline") {
      return (
        <TimelinePage
          userId={userId}
          onBack={() => setRoute("home")}
          onStart={startUploadFlow}
          onViewHistory={() => setRoute("history")}
          onViewComparison={() => setRoute("comparison")}
        />
      );
    }

    if (route === "profile") {
      return (
        <ProfilePage
          userId={userId}
          onBack={() => setRoute("home")}
          onStart={startUploadFlow}
          onViewHistory={() => setRoute("history")}
          onViewTimeline={() => setRoute("timeline")}
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
        onViewTimeline={() => setRoute("timeline")}
      />
    );
  })();

  return <SessionContext.Provider value={sessionValue}>{appBody}</SessionContext.Provider>;
}
