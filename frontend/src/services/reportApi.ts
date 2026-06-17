import { apiClient } from "./apiClient";
import type { ReportComparisonResponse, ReportEvaluationResponse, ReportHistoryResponse, ReportResponse } from "../types/aesthetic";

export function getReport(reportId: string) {
  return apiClient<ReportResponse>(`/api/reports/${reportId}`);
}

export function getReportHistory(userId: string, limit = 20, offset = 0) {
  return apiClient<ReportHistoryResponse>(`/api/users/${userId}/reports?limit=${limit}&offset=${offset}`);
}

export function getLatestReportComparison(userId: string) {
  return apiClient<ReportComparisonResponse>(`/api/users/${userId}/reports/comparison/latest`);
}

export function getReportEvaluation(reportId: string) {
  return apiClient<ReportEvaluationResponse>(`/api/reports/${reportId}/evaluation`);
}
