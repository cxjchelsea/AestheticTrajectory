import { apiClient } from "./apiClient";

export type ExternalSourceConnectionStatus =
  | "pending_authorization"
  | "connected"
  | "disconnected"
  | "expired"
  | "revoked"
  | "failed";

export interface ExternalSourceConnection {
  id: string;
  userId: string;
  provider: string;
  status: ExternalSourceConnectionStatus;
  scopes: string[];
  resourceUri?: string | null;
  tokenExpiresAt?: string | null;
  lastConnectedAt?: string | null;
  lastError?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ExternalSourceListResponse {
  userId: string;
  runtime: string;
  connections: ExternalSourceConnection[];
  total: number;
}

export interface ExternalSourceConnectResponse {
  provider: string;
  authorizationUrl: string;
  state: string;
  status: ExternalSourceConnectionStatus;
}

export interface ExternalContextItem {
  id: string;
  batchId: string;
  userId: string;
  title: string;
  snippet: string;
  sourceUri?: string | null;
  tags: string[];
  createdAt: string;
}

export interface ExternalImportBatch {
  id: string;
  userId: string;
  sourceSystem: string;
  status: "pending_confirmation" | "confirmed" | "rejected";
  itemCount: number;
  items: ExternalContextItem[];
  confirmedAt?: string | null;
  createdAt: string;
  disclaimer: string;
}

export function listExternalSources(userId: string) {
  return apiClient<ExternalSourceListResponse>(`/api/users/${userId}/external-sources`);
}

export function connectExternalSource(userId: string, provider: string) {
  return apiClient<ExternalSourceConnectResponse>(`/api/users/${userId}/external-sources/${provider}/connect`, {
    method: "POST",
  });
}

export function completeExternalSourceCallback(authorizationUrl: string) {
  return apiClient<ExternalSourceConnection>(authorizationUrl);
}

export function disconnectExternalSource(userId: string, provider: string) {
  return apiClient<ExternalSourceConnection>(`/api/users/${userId}/external-sources/${provider}/disconnect`, {
    method: "POST",
  });
}

export function previewExternalImport(userId: string, provider: string, limit = 3) {
  return apiClient<ExternalImportBatch>(`/api/users/${userId}/external-sources/${provider}/imports/preview`, {
    method: "POST",
    body: JSON.stringify({ limit }),
  });
}

export function confirmExternalImport(userId: string, batchId: string) {
  return apiClient<ExternalImportBatch>(`/api/users/${userId}/external-imports/${batchId}/confirm`, {
    method: "POST",
  });
}

export function rejectExternalImport(userId: string, batchId: string) {
  return apiClient<ExternalImportBatch>(`/api/users/${userId}/external-imports/${batchId}/reject`, {
    method: "POST",
  });
}
