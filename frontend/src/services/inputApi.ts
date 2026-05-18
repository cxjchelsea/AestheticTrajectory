import { apiClient } from "./apiClient";
import type { AestheticInput } from "../types/aesthetic";

export function createInput(input: Omit<AestheticInput, "id">) {
  return apiClient<AestheticInput>("/api/inputs", {
    method: "POST",
    body: JSON.stringify(input)
  });
}
