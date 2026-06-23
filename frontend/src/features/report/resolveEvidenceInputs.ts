import type { AestheticInput, InputFeature, ReportResponse } from "../../types/aesthetic";

export function resolveEvidenceInputs(report: ReportResponse, inputs: AestheticInput[]): AestheticInput[] {
  const byId = new Map(inputs.map((input) => [input.id, input]));

  return report.lowLevelFeatures.map((feature) => {
    const existing = byId.get(feature.inputId);
    if (existing) {
      return existing;
    }
    return inputFromFeature(feature);
  });
}

function inputFromFeature(feature: InputFeature): AestheticInput {
  const samples = feature.sampleEvidence.map((item) => item.trim()).filter(Boolean);
  const title = samples[0] || feature.inputId;
  const body = samples.slice(1).join("；");

  return {
    id: feature.inputId,
    type: feature.featureType,
    title,
    contentText: body || undefined,
  };
}
