import { apiClient } from "./apiClient";
import type { ReportResponse } from "../types/aesthetic";

export function getReport(reportId: string) {
  return apiClient<ReportResponse>(`/api/reports/${reportId}`);
}
