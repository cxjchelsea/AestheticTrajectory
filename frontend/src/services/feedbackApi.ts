import { apiClient } from "./apiClient";
import type { FeedbackRating, InsightFeedbackResponse } from "../types/aesthetic";

export function submitInsightFeedback(insightId: string, rating: FeedbackRating, comment?: string) {
  return apiClient<InsightFeedbackResponse>(`/api/insights/${insightId}/feedback`, {
    method: "POST",
    body: JSON.stringify({ rating, comment })
  });
}

export function getInsightFeedback(insightId: string) {
  return apiClient<InsightFeedbackResponse | null>(`/api/insights/${insightId}/feedback`);
}
