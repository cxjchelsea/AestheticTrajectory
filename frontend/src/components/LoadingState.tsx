interface LoadingStateProps {
  label: string;
}

export function LoadingState({ label }: LoadingStateProps) {
  return (
    <div className="loading-state" aria-live="polite">
      <span className="loader" />
      <span>{label}</span>
    </div>
  );
}
