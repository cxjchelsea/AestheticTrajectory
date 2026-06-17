export type AppRoute = "home" | "upload" | "analysis" | "report" | "history" | "profile";

export type InputType = "image" | "text";

export interface AestheticInput {
  id: string;
  type: InputType;
  title: string;
  contentText?: string;
  fileUrl?: string;
  description?: string;
}

export interface FeatureSignal {
  value: string;
  confidence: number;
  evidence: string[];
}

export interface InputFeature {
  inputId: string;
  featureType: InputType;
  lowLevelFeatures: Record<string, FeatureSignal>;
  sampleEvidence: string[];
  promptVersion: string;
  modelName: string;
}

export interface SimilarityGroup {
  groupId: string;
  name: string;
  inputIds: string[];
  commonFeatures: string[];
  uncertainty: string;
}

export interface PossibleInterpretation {
  id: string;
  name: string;
  confidence: number;
  evidenceRefs: string[];
  uncertainty: string;
}

export interface Insight {
  insightId: string;
  title: string;
  observation: string;
  evidenceRefs: string[];
  interpretation: string;
  uncertainty: string;
  confidence: number;
}

export interface ReportResponse {
  reportId: string;
  title: string;
  summary: string;
  lowLevelFeatures: InputFeature[];
  similarityGroups: SimilarityGroup[];
  possibleInterpretations: PossibleInterpretation[];
  insights: Insight[];
  disclaimer: string;
}

export interface ReportSummary {
  reportId: string;
  jobId: string | null;
  title: string;
  summary: string;
  inputCount: number;
  createdAt: string;
}

export interface ReportHistoryResponse {
  reports: ReportSummary[];
  total: number;
  limit: number;
  offset: number;
}

export type FeedbackRating = "not_me" | "unsure" | "somewhat_me" | "very_me";

export interface InsightFeedbackResponse {
  id: string;
  userId: string;
  insightId: string;
  interpretationId?: string | null;
  rating: FeedbackRating;
  comment?: string | null;
  createdAt: string;
}

export type ProfileItemStatus = "stable" | "recent" | "rejected" | "uncertain" | "inactive" | "hidden" | "deleted";

export type ProfileEvidenceType = "feature" | "report" | "interpretation" | "insight" | "feedback";

export type ProfileEvidenceDirection = "positive" | "negative" | "uncertain" | "conflict";

export interface ProfileEvidence {
  id: string;
  evidenceType: ProfileEvidenceType;
  evidenceId: string;
  direction: ProfileEvidenceDirection;
  weightDelta: number;
  note: string;
  createdAt: string;
}

export interface ProfileItem {
  id: string;
  key: string;
  label: string;
  status: ProfileItemStatus;
  weight: number;
  confidence: number;
  sourceCount: number;
  lastSeenAt: string;
  evidence: ProfileEvidence[];
}

export interface UserProfile {
  id: string;
  summary: string;
  version: string;
  items: ProfileItem[];
  updatedAt: string;
}

export interface ProfileResponse {
  userId: string;
  profile: UserProfile | null;
  message?: string | null;
}

export type AnalysisLogStatus = "running" | "success" | "failed" | "skipped";

export interface AnalysisLogRecord {
  id: string;
  jobId: string;
  stepId: string;
  status: AnalysisLogStatus;
  modelName?: string | null;
  promptVersion?: string | null;
  latencyMs?: number | null;
  errorType?: string | null;
  errorMessage?: string | null;
  startedAt?: string | null;
  finishedAt?: string | null;
  createdAt: string;
}

export interface FallbackEvent {
  id: string;
  jobId: string;
  stepId: string;
  fallbackType: string;
  originalError: string;
  fallbackAction: string;
  severity: "info" | "warning" | "error";
  userVisible: boolean;
  developerMessage: string;
  createdAt: string;
}

export interface MockUsageRecord {
  component: string;
  status: "enabled" | "disabled";
  devOnly: boolean;
  developerMessage: string;
}

export interface SchemaValidationRecord {
  stepId: string;
  schemaName: string;
  status: "passed" | "failed" | "not_recorded";
  developerMessage: string;
}

export interface BoundaryWarning {
  capability: string;
  status: "not_used" | "planned" | "dev_only";
  developerMessage: string;
}

export interface AnalysisJobDebugResponse {
  jobId: string;
  status: string;
  workflowTrace: AnalysisLogRecord[];
  fallbackEvents: FallbackEvent[];
  mockUsage: MockUsageRecord[];
  schemaValidation: SchemaValidationRecord[];
  boundaryWarnings: BoundaryWarning[];
}
