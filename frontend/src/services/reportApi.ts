import { apiClient } from "./apiClient";
import type { ReportHistoryResponse, ReportResponse } from "../types/aesthetic";

export function getReport(reportId: string) {
  return apiClient<ReportResponse>(`/api/reports/${reportId}`);
}

export function getReportHistory(userId: string, limit = 20, offset = 0) {
  return apiClient<ReportHistoryResponse>(`/api/users/${userId}/reports?limit=${limit}&offset=${offset}`);
}
