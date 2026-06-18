import { Button } from "../components/Button";

interface HomePageProps {
  onStart: () => void;
  onViewDemo: () => void;
  onViewHistory: () => void;
  onViewProfile: () => void;
  onViewTimeline: () => void;
}

export function HomePage({ onStart, onViewDemo, onViewHistory, onViewProfile, onViewTimeline }: HomePageProps) {
  return (
    <main className="page home-page">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Aesthetic Trajectory V0</p>
          <h1>审美轨迹</h1>
          <p className="lead">上传一组图像或文字样本，得到一份基于证据的审美观察报告。</p>
          <div className="hero-actions">
            <Button onClick={onStart}>开始上传</Button>
            <Button variant="secondary" onClick={onViewDemo}>查看示例报告</Button>
            <Button variant="secondary" onClick={onViewHistory}>查看历史报告</Button>
            <Button variant="secondary" onClick={onViewProfile}>查看轻量画像</Button>
            <Button variant="secondary" onClick={onViewTimeline}>查看审美时间轴</Button>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="visual-panel panel-a" />
          <div className="visual-panel panel-b" />
          <div className="visual-panel panel-c" />
        </div>
      </section>

      <section className="insight-strip">
        <article>
          <strong>示例洞察</strong>
          <span>你近期可能更容易被安静、低密度的视觉结构吸引。</span>
        </article>
        <article>
          <strong>边界说明</strong>
          <span>报告只描述当前输入中的审美结构，不做心理诊断或长期画像。</span>
        </article>
      </section>
    </main>
  );
}
