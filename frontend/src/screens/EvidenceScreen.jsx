import Card, { DataRow } from "../components/Card.jsx";

export default function EvidenceScreen({ result, onNext }) {
  if (!result) return null;
  const { violation_id, vehicle_type, violation_label, plate, timestamp, annotated_image_url } = result;
  const time = new Date(timestamp);
  const formatted = time.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <p className="eyebrow mb-2">Screen 04 — Evidence Card</p>
      <h1 className="font-display text-3xl font-semibold mb-6">Violation Evidence</h1>

      <Card className="overflow-hidden p-0">
        <img src={annotated_image_url} alt="evidence" className="w-full" />
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <span className="font-display text-cyan text-lg tracking-wide">
              VISIONGUARD AI — EVIDENCE
            </span>
            <span className="font-mono text-xs text-textmuted">e-Challan ready</span>
          </div>
          <div className="grid grid-cols-2 gap-y-5 gap-x-6">
            <DataRow label="Violation ID" value={violation_id} accent />
            <DataRow label="Vehicle" value={vehicle_type} />
            <DataRow label="Violation" value={violation_label} />
            <DataRow label="Plate" value={plate.text || "UNREADABLE"} />
            <DataRow label="Time" value={formatted} />
          </div>
        </div>
      </Card>

      <button
        onClick={onNext}
        className="mt-6 bg-cyan text-base font-mono font-medium px-6 py-3 rounded-lg hover:opacity-90 transition-opacity"
      >
        Compute Risk Score →
      </button>
    </div>
  );
}
