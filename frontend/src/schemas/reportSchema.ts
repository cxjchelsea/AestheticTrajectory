import type { ReportResponse } from "../types/aesthetic";

export function isReportResponse(value: unknown): value is ReportResponse {
  if (!value || typeof value !== "object") return false;
  const report = value as Partial<ReportResponse>;
  return (
    typeof report.reportId === "string" &&
    typeof report.title === "string" &&
    typeof report.summary === "string" &&
    Array.isArray(report.lowLevelFeatures) &&
    Array.isArray(report.similarityGroups) &&
    Array.isArray(report.possibleInterpretations) &&
    Array.isArray(report.insights)
  );
}
