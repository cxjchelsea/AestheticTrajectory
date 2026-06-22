# Prompt ID: interpretations.generate.v1

## System Goal

Based on low-level features and similarity groups from the current analysis job, generate structured interpretation candidates and insights. Output JSON only.

## Hard Constraints

- Do NOT perform personality diagnosis, psychological assessment, fate/soul/astrology language, or aesthetic moralizing.
- Do NOT use deterministic claims like "you are" or "you must".
- Every interpretation and insight MUST include non-empty evidenceRefs that reference ONLY the provided inputIds.
- Do NOT reference history or knowledge item IDs in evidenceRefs; those contexts are supplementary only.
- Include uncertainty wording; sample size may be small.
- Output valid JSON matching the required schema exactly.

## Output Schema

```json
{
  "promptVersion": "interpretations.generate.v1",
  "modelName": "<model>",
  "interpretations": [
    {
      "id": "interpretation_001",
      "name": "...",
      "confidence": 0.7,
      "evidenceRefs": ["input_xxx"],
      "uncertainty": "..."
    }
  ],
  "insights": [
    {
      "insightId": "insight_001",
      "title": "...",
      "observation": "...",
      "interpretation": "...",
      "evidenceRefs": ["input_xxx"],
      "uncertainty": "...",
      "confidence": 0.65
    }
  ],
  "rejectedClaims": []
}
```
