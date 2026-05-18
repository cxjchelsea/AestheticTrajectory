import { apiClient } from "./apiClient";

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
