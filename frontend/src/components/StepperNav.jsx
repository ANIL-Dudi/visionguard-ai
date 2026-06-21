const STEPS = [
  { key: "upload", label: "Upload" },
  { key: "detection", label: "Detection" },
  { key: "plate", label: "Plate" },
  { key: "evidence", label: "Evidence" },
  { key: "risk", label: "Risk" },
  { key: "dashboard", label: "Dashboard" },
];

export default function StepperNav({ current, onJump, maxReached }) {
  const currentIdx = STEPS.findIndex((s) => s.key === current);
  const maxIdx = STEPS.findIndex((s) => s.key === maxReached);

  return (
    <div className="flex items-center gap-0 overflow-x-auto px-6 py-4 border-b border-border bg-panel">
      {STEPS.map((step, i) => {
        const isActive = step.key === current;
        const isReachable = i <= maxIdx;
        return (
          <div key={step.key} className="flex items-center">
            <button
              disabled={!isReachable}
              onClick={() => isReachable && onJump(step.key)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-mono transition-colors ${
                isActive
                  ? "bg-cyan/10 text-cyan border border-cyan"
                  : isReachable
                  ? "text-textmuted hover:text-textprimary border border-transparent"
                  : "text-textmuted/40 border border-transparent cursor-not-allowed"
              }`}
            >
              <span className="text-xs">{String(i + 1).padStart(2, "0")}</span>
              <span className="hidden sm:inline">{step.label}</span>
            </button>
            {i < STEPS.length - 1 && (
              <div
                className={`w-6 h-px mx-1 ${i < currentIdx ? "bg-cyan/50" : "bg-border"}`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export { STEPS };
