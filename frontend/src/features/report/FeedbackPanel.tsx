import { useState } from "react";
import { Button } from "../../components/Button";
import { submitInsightFeedback } from "../../services/feedbackApi";
import type { FeedbackRating } from "../../types/aesthetic";

const ratings: Array<{ value: FeedbackRating; label: string }> = [
  { value: "not_me", label: "不像我" },
  { value: "unsure", label: "不确定" },
  { value: "somewhat_me", label: "有点像" },
  { value: "very_me", label: "很像我" }
];

interface FeedbackPanelProps {
  insightId: string;
}

export function FeedbackPanel({ insightId }: FeedbackPanelProps) {
  const [selected, setSelected] = useState<FeedbackRating | null>(null);
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "local">("idle");

  async function submit(rating: FeedbackRating) {
    setSelected(rating);
    setStatus("saving");
    try {
      await submitInsightFeedback(insightId, rating);
      setStatus("saved");
    } catch {
      setStatus("local");
    }
  }

  return (
    <div className="feedback-panel">
      <span>这条洞察像你吗？</span>
      <div className="segmented">
        {ratings.map((rating) => (
          <Button
            type="button"
            variant={selected === rating.value ? "primary" : "secondary"}
            key={rating.value}
            onClick={() => submit(rating.value)}
          >
            {rating.label}
          </Button>
        ))}
      </div>
      {status === "saved" ? <small>已保存反馈</small> : null}
      {status === "local" ? <small>后端不可用，反馈仅保留在当前界面</small> : null}
    </div>
  );
}
