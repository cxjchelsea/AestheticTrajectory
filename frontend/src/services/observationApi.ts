import { apiClient } from "./apiClient";

export interface ObservationQuestion {
  text: string;
  evidenceRefs: string[];
}

export interface ObservationSession {
  id: string;
  userId: string;
  status: "running" | "completed" | "abstained" | "failed";
  triggerSource: string;
  period?: "week" | "month" | null;
  summary?: string | null;
  questions: ObservationQuestion[];
  evidenceRefs: string[];
  message?: string | null;
  disclaimer: string;
  createdAt: string;
  finishedAt?: string | null;
}

export interface AgentActionLog {
  id: string;
  userId: string;
  sessionId: string;
  stepIndex: number;
  toolName: string;
  reason: string;
  inputRefs: string[];
  outputRefs: string[];
  status: string;
  latencyMs?: number | null;
  createdAt: string;
}

export interface AgentActionListResponse {
  userId: string;
  actions: AgentActionLog[];
  total: number;
  sessionId?: string | null;
}

export function createObservation(userId: string, triggerSource = "profile_page", period: "week" | "month" = "week") {
  return apiClient<ObservationSession>(`/api/users/${userId}/observations`, {
    method: "POST",
    body: JSON.stringify({ triggerSource, period }),
  });
}

export function getObservation(userId: string, sessionId: string) {
  return apiClient<ObservationSession>(`/api/users/${userId}/observations/${sessionId}`);
}

export function listAgentActions(userId: string, sessionId?: string) {
  const query = sessionId ? `?sessionId=${encodeURIComponent(sessionId)}` : "";
  return apiClient<AgentActionListResponse>(`/api/users/${userId}/agent-actions${query}`);
}
