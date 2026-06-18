import { useState } from "react";
import { Button } from "../../components/Button";
import { uploadFile } from "../../services/fileApi";
import type { AestheticInput } from "../../types/aesthetic";

interface UploadFormProps {
  onAdd: (input: AestheticInput) => void;
}

export function UploadForm({ onAdd }: UploadFormProps) {
  const [text, setText] = useState("");
  const [musicTitle, setMusicTitle] = useState("");
  const [musicUrl, setMusicUrl] = useState("");
  const [videoTitle, setVideoTitle] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

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

  async function handleImageUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    try {
      const uploaded = await uploadFile(file);
      onAdd({
        id: `input_${Date.now()}`,
        type: "image",
        title: file.name,
        fileUrl: uploaded.fileUrl,
        description: `已上传图片（${uploaded.mimeType}，${uploaded.sizeBytes} bytes）`
      });
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "图片上传失败");
    } finally {
      setUploading(false);
    }
  }

  function addMusicInput() {
    const title = musicTitle.trim();
    const url = musicUrl.trim();
    if (!title && !url) return;

    onAdd({
      id: `input_${Date.now()}`,
      type: "music",
      title: title || "音乐样本",
      fileUrl: url || undefined,
      description: "V4-A 仅记录音乐元数据，尚未解析音频内容。"
    });
    setMusicTitle("");
    setMusicUrl("");
  }

  function addVideoInput() {
    const title = videoTitle.trim();
    const url = videoUrl.trim();
    if (!title && !url) return;

    onAdd({
      id: `input_${Date.now()}`,
      type: "video",
      title: title || "视频样本",
      fileUrl: url || undefined,
      description: "V4-A 仅记录视频元数据，尚未解析视频内容。"
    });
    setVideoTitle("");
    setVideoUrl("");
  }

  return (
    <div className="upload-form">
      <div className="dropzone">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          aria-label="上传图片"
          disabled={uploading}
        />
        <div>
          <strong>图片样本</strong>
          <span>{uploading ? "正在上传..." : "选择图片后上传到后端文件存储"}</span>
        </div>
      </div>
      {uploadError ? <p className="muted">{uploadError}</p> : null}

      <label className="field">
        <span>文字样本</span>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="粘贴一段喜欢的文字、描述或观察..."
          rows={6}
        />
      </label>
      <Button type="button" variant="secondary" onClick={addTextInput}>
        添加文字样本
      </Button>

      <label className="field">
        <span>音乐样本（元数据）</span>
        <input
          value={musicTitle}
          onChange={(event) => setMusicTitle(event.target.value)}
          placeholder="曲名或歌单标题"
        />
        <input
          value={musicUrl}
          onChange={(event) => setMusicUrl(event.target.value)}
          placeholder="可选：链接或 fileUrl"
        />
      </label>
      <Button type="button" variant="secondary" onClick={addMusicInput}>
        添加音乐样本
      </Button>

      <label className="field">
        <span>视频样本（元数据）</span>
        <input
          value={videoTitle}
          onChange={(event) => setVideoTitle(event.target.value)}
          placeholder="片名或片段标题"
        />
        <input
          value={videoUrl}
          onChange={(event) => setVideoUrl(event.target.value)}
          placeholder="可选：链接或 fileUrl"
        />
      </label>
      <Button type="button" variant="secondary" onClick={addVideoInput}>
        添加视频样本
      </Button>
    </div>
  );
}
