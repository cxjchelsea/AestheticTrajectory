import type { ReactNode } from "react";

interface ReportSectionProps {
  title: string;
  children: ReactNode;
}

export function ReportSection({ title, children }: ReportSectionProps) {
  return (
    <section className="report-section">
      <h2>{title}</h2>
      {children}
    </section>
  );
}
