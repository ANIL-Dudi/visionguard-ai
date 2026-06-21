import Card from "../components/Card.jsx";
import Badge, { riskTone } from "../components/Badge.jsx";

export default function RiskScreen({ result, onNext }) {
  if (!result) return null;
  const { risk, recommendation, violation_label } = result;
  const tone = riskTone(risk.level);
  const pct = Math.min(100, risk.score);

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <p className="eyebrow mb-2">Screen 05 — Risk Score</p>
      <h1 className="font-display text-3xl font-semibold mb-6">Risk Assessment</h1>

      <Card className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <span className="font-mono text-textmuted">{violation_label}</span>
          <Badge tone={tone}>{risk.level} Risk</Badge>
        </div>

        <div className="flex items-end gap-3">
          <span className="font-display text-6xl font-bold text-textprimary">{risk.score}</span>
          <span className="text-textmuted font-mono mb-2">/ 100</span>
        </div>

        <div className="h-3 rounded-full bg-border overflow-hidden">
          <div
            className={`h-full rounded-full ${
              tone === "red" ? "bg-red" : tone === "amber" ? "bg-amber" : "bg-cyan"
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>

        <div className="grid grid-cols-3 gap-4 pt-2 font-mono text-sm">
          <div>
            <p className="text-textmuted text-xs uppercase mb-1">Base</p>
            <p className="text-textprimary text-lg">{risk.base_score}</p>
          </div>
          <div>
            <p className="text-textmuted text-xs uppercase mb-1">Repeat bonus</p>
            <p className="text-textprimary text-lg">+{risk.repeat_offender_bonus}</p>
          </div>
          <div>
            <p className="text-textmuted text-xs uppercase mb-1">Conf. penalty</p>
            <p className="text-textprimary text-lg">{risk.confidence_penalty}</p>
          </div>
        </div>

        <div className="border-t border-border pt-4">
          <p className="text-xs font-mono uppercase tracking-wider text-textmuted mb-2">
            Officer Recommendation
          </p>
          <p className="text-textprimary leading-relaxed">{recommendation}</p>
        </div>
      </Card>

      <button
        onClick={onNext}
        className="mt-6 bg-cyan text-base font-mono font-medium px-6 py-3 rounded-lg hover:opacity-90 transition-opacity"
      >
        Open Dashboard →
      </button>
    </div>
  );
}
