import { Button } from "../../components/Button";
import type { AestheticInput } from "../../types/aesthetic";

interface InputPreviewListProps {
  inputs: AestheticInput[];
  onRemove: (id: string) => void;
}

export function InputPreviewList({ inputs, onRemove }: InputPreviewListProps) {
  return (
    <div className="preview-list">
      {inputs.map((input) => (
        <article className="preview-item" key={input.id}>
          <div className={`sample-thumb sample-${input.type}`}>{input.type === "image" ? "图" : "文"}</div>
          <div>
            <h3>{input.title}</h3>
            <p>{input.description ?? input.contentText}</p>
          </div>
          <Button type="button" variant="ghost" onClick={() => onRemove(input.id)} aria-label={`删除 ${input.title}`}>
            删除
          </Button>
        </article>
      ))}
    </div>
  );
}
