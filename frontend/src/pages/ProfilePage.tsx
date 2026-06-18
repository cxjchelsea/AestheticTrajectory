import { useEffect, useState } from "react";
import { Button } from "../components/Button";
import { getUserProfile } from "../services/profileApi";
import type { ProfileEvidence, ProfileItem, ProfileResponse } from "../types/aesthetic";

interface ProfilePageProps {
  userId: string;
  onBack: () => void;
  onStart: () => void;
  onViewHistory: () => void;
  onViewTimeline?: () => void;
}

export function ProfilePage({ userId, onBack, onStart, onViewHistory, onViewTimeline }: ProfilePageProps) {
  const [profileResponse, setProfileResponse] = useState<ProfileResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      try {
        setStatus("loading");
        const response = await getUserProfile(userId);
        if (cancelled) return;
        setProfileResponse(response);
        setStatus("ready");
      } catch (error) {
        if (cancelled) return;
        setErrorMessage(error instanceof Error ? error.message : "API request failed");
        setStatus("error");
      }
    }

    loadProfile();
    return () => {
      cancelled = true;
    };
  }, [userId]);

  const profile = profileResponse?.profile ?? null;
  const totalEvidence = profile?.items.reduce((sum, item) => sum + item.sourceCount, 0) ?? 0;
  const feedbackEvidence = profile?.items.reduce(
    (sum, item) => sum + item.evidence.filter((evidence) => evidence.evidenceType === "feedback").length,
    0
  ) ?? 0;
  const positiveItems = profile?.items.filter((item) => item.status === "stable" || item.status === "recent") ?? [];
  const correctionItems = profile?.items.filter(
    (item) => item.status === "rejected" || item.status === "uncertain"
  ) ?? [];

  return (
    <main className="page profile-page">
      <div className="report-header">
        <div>
          <p className="eyebrow">V2-B Profile</p>
          <h1>轻量画像</h1>
          <p className="lead">基于历史报告、洞察和反馈生成的只读审美倾向摘要。每个条目都必须能追溯到 evidence。</p>
        </div>
        <div className="hero-actions">
          <Button variant="secondary" onClick={onBack}>返回首页</Button>
          <Button variant="secondary" onClick={onViewHistory}>历史报告</Button>
          {onViewTimeline ? <Button variant="secondary" onClick={onViewTimeline}>审美时间轴</Button> : null}
          <Button onClick={onStart}>开始一次分析</Button>
        </div>
      </div>

      {status === "loading" ? <p className="muted">正在读取轻量画像...</p> : null}

      {status === "error" ? (
        <section className="empty-state">
          <h2>暂时无法读取轻量画像</h2>
          <p>{errorMessage}</p>
          <Button variant="secondary" onClick={onBack}>返回首页</Button>
        </section>
      ) : null}

      {status === "ready" && !profile ? (
        <section className="empty-state">
          <h2>还没有足够证据生成画像</h2>
          <p>{profileResponse?.message ?? "完成几次分析或提交反馈后，这里会显示可追溯的轻量画像。"}</p>
          <Button onClick={onStart}>开始一次分析</Button>
        </section>
      ) : null}

      {status === "ready" && profile ? (
        <>
          <section className="profile-summary">
            <p className="eyebrow">画像摘要 · {profile.version}</p>
            <h2>{humanizeSummary(profile.summary, positiveItems)}</h2>
            <p className="muted">
              已汇总 {profile.items.length} 个倾向条目、{totalEvidence} 条支撑证据，其中 {feedbackEvidence} 条来自你的反馈。
              该画像只描述输入中出现的审美倾向，不做人格、心理或能力判断。
            </p>
            <small className="muted">最近更新 {new Date(profile.updatedAt).toLocaleString()}</small>
          </section>

          {correctionItems.length > 0 ? (
            <section className="profile-list" aria-label="已否定或待确认的解释">
              <div className="section-heading">
                <p className="eyebrow">Feedback Corrections</p>
                <h2>你已否定或待确认的解释</h2>
                <p className="muted">这些记录不会进入正向画像摘要，但会用于提醒系统后续不要继续强化不符合你的解释。</p>
              </div>
              {correctionItems.map((item) => (
                <ProfileItemCard item={item} key={item.id} correction />
              ))}
            </section>
          ) : null}

          <section className="profile-list" aria-label="画像条目列表">
            <div className="section-heading">
              <p className="eyebrow">Profile Items</p>
              <h2>倾向条目</h2>
              <p className="muted">这里只展示系统当前认为可以作为正向画像的倾向；被你否定或仍不确定的解释会单独放在下方。</p>
            </div>
            {positiveItems.length > 0 ? positiveItems.map((item) => (
              <ProfileItemCard item={item} key={item.id} />
            )) : (
              <section className="empty-state">
                <h2>暂时没有正向画像条目</h2>
                <p>系统目前只记录到被否定或仍不确定的解释，还不会把它们写成你的审美倾向。</p>
              </section>
            )}
          </section>
        </>
      ) : null}
    </main>
  );
}

function ProfileItemCard({ item, correction = false }: { item: ProfileItem; correction?: boolean }) {
  return (
    <article className={correction ? "profile-card profile-card-correction" : "profile-card"}>
      <div className="profile-card-header">
        <div>
          <p className="eyebrow">{statusLabel(item.status)}</p>
          <h2>{humanizeProfileLabel(item.label)}</h2>
        </div>
        <small>{item.sourceCount} 条证据 · 可信度 {Math.round(item.confidence * 100)}%</small>
      </div>
      <p className="muted">倾向强度 {formatWeight(item.weight)} · 最近出现 {new Date(item.lastSeenAt).toLocaleString()}</p>
      {item.evidence.some((evidence) => evidence.evidenceType === "feedback") ? (
        <p className={correction ? "feedback-callout feedback-callout-correction" : "feedback-callout"}>
          {correction ? "这条解释已被你的反馈修正，不会作为正向画像强化。" : "包含来自你反馈的证据。"}
        </p>
      ) : null}
      <div className="evidence-heading">
        <h3>{correction ? "修正证据" : "支撑证据"}</h3>
        <span>Evidence refs</span>
      </div>
      <div className="evidence-stack">
        {item.evidence.slice(0, 4).map((evidence) => (
          <div className="evidence-chip" key={evidence.id}>
            <div className="evidence-chip-header">
              <strong>{directionLabel(evidence.direction)}</strong>
              <span>{evidenceTypeLabel(evidence.evidenceType)}</span>
            </div>
            <p>{humanizeEvidenceNote(evidence)}</p>
            <small className="muted">证据引用：{shortEvidenceRef(evidence)}</small>
          </div>
        ))}
        {item.evidence.length > 4 ? (
          <p className="muted">另有 {item.evidence.length - 4} 条证据已折叠。</p>
        ) : null}
      </div>
    </article>
  );
}

function humanizeSummary(summary: string, items: ProfileItem[]) {
  if (!summary.includes("=")) return summary;
  const labels = items.slice(0, 3).map((item) => humanizeProfileLabel(item.label));
  if (!labels.length) return "系统正在基于可追溯证据整理你的轻量画像。";
  return `系统观察到你近期输入中反复出现 ${labels.join("、")} 等审美倾向。`;
}

function humanizeProfileLabel(label: string) {
  if (label.startsWith("density:")) {
    return `画面密度偏${featureValueLabel(label.replace("density:", "").trim())}`;
  }
  if (label.startsWith("presence:")) {
    return presenceLabel(label.replace("presence:", "").trim());
  }
  return label
    .replace(/density=([a-z_]+)/g, (_, value: string) => `画面密度偏${featureValueLabel(value)}`)
    .replace(/presence=([a-z_]+)/g, (_, value: string) => presenceLabel(value));
}

function humanizeEvidenceNote(evidence: ProfileEvidence) {
  const note = evidence.note
    .replace(/用户反馈 ([a-z_]+):/g, (_, rating: string) => `用户反馈“${ratingLabel(rating)}”：`)
    .replace(/density=([a-z_]+)/g, (_, value: string) => `画面密度偏${featureValueLabel(value)}`)
    .replace(/presence=([a-z_]+)/g, (_, value: string) => presenceLabel(value));

  if (evidence.evidenceType === "feature") {
    return `来自历史报告的视觉特征：${note}`;
  }
  if (evidence.evidenceType === "feedback") {
    return note;
  }
  return note;
}

function statusLabel(status: ProfileItem["status"]) {
  const labels: Record<ProfileItem["status"], string> = {
    stable: "稳定倾向",
    recent: "近期出现",
    weakening: "近期减弱",
    rejected: "已被否定",
    uncertain: "仍不确定",
    inactive: "暂不活跃",
    hidden: "已隐藏",
    deleted: "已删除"
  };
  return labels[status];
}

function evidenceTypeLabel(type: ProfileEvidence["evidenceType"]) {
  const labels: Record<ProfileEvidence["evidenceType"], string> = {
    feature: "来自历史报告",
    report: "来自报告",
    interpretation: "来自解释",
    insight: "来自洞察",
    feedback: "来自用户反馈"
  };
  return labels[type];
}

function directionLabel(direction: ProfileEvidence["direction"]) {
  const labels: Record<ProfileEvidence["direction"], string> = {
    positive: "支持该倾向",
    negative: "反向证据",
    uncertain: "不确定证据",
    conflict: "冲突证据"
  };
  return labels[direction];
}

function ratingLabel(rating: string) {
  const labels: Record<string, string> = {
    not_me: "不像我",
    unsure: "不确定",
    somewhat_me: "比较符合我",
    very_me: "很符合我"
  };
  return labels[rating] ?? rating;
}

function featureValueLabel(value: string) {
  const labels: Record<string, string> = {
    low: "低",
    medium: "中等",
    high: "高"
  };
  return labels[value] ?? value;
}

function presenceLabel(value: string) {
  const labels: Record<string, string> = {
    person_absent: "较少出现人物主体",
    person_present: "经常出现人物主体"
  };
  return labels[value] ?? `主体出现特征：${value}`;
}

function formatWeight(weight: number) {
  if (weight > 0.6) return "较强";
  if (weight > 0.2) return "中等";
  if (weight > 0) return "较弱";
  if (weight < 0) return "反向";
  return "待观察";
}

function shortEvidenceRef(evidence: ProfileEvidence) {
  const shortId = evidence.evidenceId.length > 14 ? `${evidence.evidenceId.slice(0, 14)}...` : evidence.evidenceId;
  return `${evidenceTypeLabel(evidence.evidenceType)} / ${shortId}`;
}
