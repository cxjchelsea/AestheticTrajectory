import { useState } from "react";
import { Button } from "../../components/Button";
import type { AestheticInput } from "../../types/aesthetic";

interface UploadFormProps {
  onAdd: (input: AestheticInput) => void;
}

export function UploadForm({ onAdd }: UploadFormProps) {
  const [text, setText] = useState("");

  function addTextInput() {
    const trimmed = text.trim();
    if (!trimmed) return;

    onAdd({
      id: `input_${Date.now()}`,
      type: "text",
      title: `文本样本 ${new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}`,
      contentText: trimmed,
      description: trimmed.slice(0, 42)
    });
    setText("");
  }

  function addMockImage() {
    onAdd({
      id: `input_${Date.now()}`,
      type: "image",
      title: "图片样本",
      fileUrl: "mock://local-image",
      description: "V0 原型中先记录图片占位信息，V1 再接真实文件存储。"
    });
  }

  return (
    <div className="upload-form">
      <div className="dropzone">
        <input type="file" accept="image/*" onChange={addMockImage} aria-label="上传图片" />
        <div>
          <strong>图片样本</strong>
          <span>选择图片后生成本地 mock 预览记录</span>
        </div>
      </div>

      <label className="field">
        <span>文字样本</span>
        <textarea value={text} onChange={(event) => setText(event.target.value)} placeholder="粘贴一段喜欢的文字、描述或观察..." rows={6} />
      </label>

      <Button type="button" variant="secondary" onClick={addTextInput}>
        添加文字样本
      </Button>
    </div>
  );
}
