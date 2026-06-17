import { apiClient } from "./apiClient";
import type { ProfileResponse } from "../types/aesthetic";

export function getUserProfile(userId: string) {
  return apiClient<ProfileResponse>(`/api/users/${userId}/profile`);
}
