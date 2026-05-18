import { apiClient } from "./apiClient";
import type { FeedbackRating } from "../types/aesthetic";

export function submitInsightFeedback(insightId: string, rating: FeedbackRating, comment?: string) {
  return apiClient<{ id: string; rating: FeedbackRating }>(`/api/insights/${insightId}/feedback`, {
    method: "POST",
    body: JSON.stringify({ rating, comment })
  });
}
