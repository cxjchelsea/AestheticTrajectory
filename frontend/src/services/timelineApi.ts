import { apiClient } from "./apiClient";
import type { TimelineListResponse, TimelineSummaryResponse } from "../types/aesthetic";

export function getTimeline(userId: string, limit = 50, offset = 0) {
  return apiClient<TimelineListResponse>(`/api/users/${userId}/timeline?limit=${limit}&offset=${offset}`);
}

export function getTimelineSummary(userId: string, period: "week" | "month" = "week") {
  return apiClient<TimelineSummaryResponse>(`/api/users/${userId}/timeline/summary?period=${period}`);
}
