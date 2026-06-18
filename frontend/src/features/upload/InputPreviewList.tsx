import { Button } from "../../components/Button";
import type { AestheticInput } from "../../types/aesthetic";

interface InputPreviewListProps {
  inputs: AestheticInput[];
  onRemove: (id: string) => void;
}

const typeLabels: Record<AestheticInput["type"], string> = {
  image: "图",
  text: "文",
  music: "乐",
  video: "影"
};

export function InputPreviewList({ inputs, onRemove }: InputPreviewListProps) {
  return (
    <div className="preview-list">
      {inputs.map((input) => (
        <article className="preview-item" key={input.id}>
          <div className={`sample-thumb sample-${input.type}`}>{typeLabels[input.type]}</div>
          <div>
            <h3>{input.title}</h3>
            <p>{input.description ?? input.contentText ?? input.fileUrl}</p>
          </div>
          <Button type="button" variant="ghost" onClick={() => onRemove(input.id)} aria-label={`删除 ${input.title}`}>
            删除
          </Button>
        </article>
      ))}
    </div>
  );
}
