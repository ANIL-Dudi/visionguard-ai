const TONES = {
  cyan: "bg-cyan/10 text-cyan border-cyan/40",
  amber: "bg-amber/10 text-amber border-amber/40",
  red: "bg-red/10 text-red border-red/40",
  muted: "bg-textmuted/10 text-textmuted border-textmuted/30",
};

export default function Badge({ children, tone = "cyan" }) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono border ${TONES[tone] || TONES.cyan}`}
    >
      {children}
    </span>
  );
}

export function riskTone(level) {
  if (level === "Critical") return "red";
  if (level === "High") return "red";
  if (level === "Medium") return "amber";
  return "cyan";
}
