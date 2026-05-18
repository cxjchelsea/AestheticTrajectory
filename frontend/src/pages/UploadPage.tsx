import { Button } from "../components/Button";
import { starterInputs } from "../services/mockData";
import { InputPreviewList } from "../features/upload/InputPreviewList";
import { UploadForm } from "../features/upload/UploadForm";
import type { AestheticInput } from "../types/aesthetic";

interface UploadPageProps {
  inputs: AestheticInput[];
  onChange: (inputs: AestheticInput[]) => void;
  onStart: () => void;
  onBack: () => void;
}

export function UploadPage({ inputs, onChange, onStart, onBack }: UploadPageProps) {
  const canStart = inputs.length >= 3 && inputs.length <= 12;

  function addInput(input: AestheticInput) {
    if (inputs.length >= 12) return;
    onChange([...inputs, input]);
  }

  return (
    <main className="page two-column">
      <section>
        <button className="text-button" onClick={onBack}>返回首页</button>
        <h1>上传审美样本</h1>
        <p className="muted">至少 3 个，建议 5-10 个，最多 12 个。V0 仅使用本地 mock 数据。</p>
        <UploadForm onAdd={addInput} />
        <div className="actions-row">
          <Button variant="secondary" onClick={() => onChange(starterInputs)}>填入示例样本</Button>
          <Button onClick={onStart} disabled={!canStart}>开始分析</Button>
        </div>
      </section>
      <aside className="side-panel">
        <div className="counter">
          <strong>{inputs.length}</strong>
          <span>/ 12 个样本</span>
        </div>
        {inputs.length === 0 ? <p className="muted">还没有样本。可以先填入示例，快速跑完 V0 流程。</p> : null}
        <InputPreviewList inputs={inputs} onRemove={(id) => onChange(inputs.filter((input) => input.id !== id))} />
      </aside>
    </main>
  );
}
