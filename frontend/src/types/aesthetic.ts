export type AppRoute = "home" | "upload" | "analysis" | "report";

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

export type FeedbackRating = "not_me" | "unsure" | "somewhat_me" | "very_me";
