import { apiClient } from "./apiClient";

export type SessionBootstrapResponse = {
  userId: string;
  sessionToken: string;
  authMode: string;
};

export type SessionMeResponse = {
  userId: string;
  authMode: string;
  sessionPresent: boolean;
};

export async function bootstrapSession(): Promise<SessionBootstrapResponse> {
  return apiClient<SessionBootstrapResponse>("/api/session/bootstrap", {
    method: "POST",
    credentials: "include"
  });
}

export async function getSessionMe(): Promise<SessionMeResponse> {
  return apiClient<SessionMeResponse>("/api/session/me", {
    credentials: "include"
  });
}
