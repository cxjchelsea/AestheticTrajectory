export type AppRoute = "home" | "upload" | "analysis" | "report" | "history";

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
