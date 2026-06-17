import { useEffect, useState } from "react";
import { Button } from "../../components/Button";
import { getInsightFeedback, submitInsightFeedback } from "../../services/feedbackApi";
import type { FeedbackRating } from "../../types/aesthetic";

const ratings: Array<{ value: FeedbackRating; label: string }> = [
  { value: "not_me", label: "不像我" },
  { value: "unsure", label: "不确定" },
  { value: "somewhat_me", label: "有点像" },
  { value: "very_me", label: "很像我" }
];

interface FeedbackPanelProps {
  insightId: string;
  canPersist?: boolean;
}

export function FeedbackPanel({ insightId, canPersist = true }: FeedbackPanelProps) {
  const [selected, setSelected] = useState<FeedbackRating | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "saving" | "saved" | "local">("loading");

  useEffect(() => {
    if (!canPersist) {
      setSelected(null);
      setStatus("local");
      return;
    }

    let cancelled = false;
    setStatus("loading");
    getInsightFeedback(insightId)
      .then((feedback) => {
        if (cancelled) return;
        setSelected(feedback?.rating ?? null);
        setStatus("idle");
      })
      .catch(() => {
        if (cancelled) return;
        setSelected(null);
        setStatus("idle");
      });

    return () => {
      cancelled = true;
    };
  }, [canPersist, insightId]);

  async function submit(rating: FeedbackRating) {
    setSelected(rating);
    if (!canPersist) {
      setStatus("local");
      return;
    }

    setStatus("saving");
    try {
      const feedback = await submitInsightFeedback(insightId, rating);
      setSelected(feedback.rating);
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
            disabled={status === "loading" || status === "saving"}
          >
            {rating.label}
          </Button>
        ))}
      </div>
      {status === "loading" ? <small>正在读取已保存反馈...</small> : null}
      {status === "saved" ? <small>已保存反馈；再次选择会更新这条反馈，不会重复累计。</small> : null}
      {status === "idle" && selected ? <small>已反馈；可重新选择来修改。</small> : null}
      {status === "local" ? <small>当前报告未绑定后端洞察记录，反馈仅保留在当前界面，不会写入画像。</small> : null}
    </div>
  );
}
