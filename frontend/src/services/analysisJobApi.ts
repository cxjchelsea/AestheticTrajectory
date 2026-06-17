import { apiClient } from "./apiClient";
import type { AnalysisJobDebugResponse } from "../types/aesthetic";

export interface AnalysisJobResponse {
  id: string;
  status: string;
  inputCount: number;
  reportId?: string;
}

export function createAnalysisJob(inputIds: string[]) {
  return apiClient<AnalysisJobResponse>("/api/analysis-jobs", {
    method: "POST",
    body: JSON.stringify({ inputIds })
  });
}

export function getAnalysisJob(jobId: string) {
  return apiClient<AnalysisJobResponse>(`/api/analysis-jobs/${jobId}`);
}

export function getAnalysisJobDebug(jobId: string) {
  return apiClient<AnalysisJobDebugResponse>(`/api/analysis-jobs/${jobId}/debug`);
}
