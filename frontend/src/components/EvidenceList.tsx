import type { AestheticInput } from "../types/aesthetic";

interface EvidenceListProps {
  evidenceRefs: string[];
  inputs: AestheticInput[];
}

export function EvidenceList({ evidenceRefs, inputs }: EvidenceListProps) {
  const evidence = evidenceRefs
    .map((id) => inputs.find((input) => input.id === id))
    .filter((input): input is AestheticInput => Boolean(input));

  return (
    <ul className="evidence-list">
      {evidence.map((input) => (
        <li key={input.id}>
          <strong>{input.title}</strong>
          <span>{input.description ?? input.contentText ?? input.type}</span>
        </li>
      ))}
    </ul>
  );
}
