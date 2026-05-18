interface JobStatusPanelProps {
  activeStep: number;
}

const steps = ["读取样本", "提取底层特征", "生成向量表示", "寻找相似性结构", "生成审美报告"];

export function JobStatusPanel({ activeStep }: JobStatusPanelProps) {
  return (
    <ol className="job-steps">
      {steps.map((step, index) => (
        <li className={index <= activeStep ? "is-active" : ""} key={step}>
          <span>{index + 1}</span>
          <p>{step}</p>
        </li>
      ))}
    </ol>
  );
}
