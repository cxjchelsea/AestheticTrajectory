import type { AestheticInput } from "../types/aesthetic";

interface EvidenceListProps {
  evidenceRefs: string[];
  inputs: AestheticInput[];
}

export function EvidenceList({ evidenceRefs, inputs }: EvidenceListProps) {
  if (evidenceRefs.length === 0) {
    return null;
  }

  const inputsById = new Map(inputs.map((input) => [input.id, input]));

  return (
    <div className="evidence-block">
      <p className="evidence-label">证据引用</p>
      <ul className="evidence-list">
        {evidenceRefs.map((ref) => {
          const input = inputsById.get(ref);
          const body = input ? resolveBody(input) : null;

          return (
            <li key={ref} className="evidence-item">
              <code className="evidence-id">{ref}</code>
              {input ? (
                <>
                  {input.title ? <strong>{input.title}</strong> : null}
                  {body ? <p className="evidence-body">{body}</p> : null}
                </>
              ) : (
                <p className="evidence-body muted">未找到对应样本详情</p>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function resolveBody(input: AestheticInput): string | null {
  const candidates = [input.contentText, input.description].filter(Boolean) as string[];
  for (const candidate of candidates) {
    if (candidate !== input.title) {
      return candidate;
    }
  }
  return null;
}
