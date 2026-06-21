import Card, { DataRow } from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import BoundingBoxOverlay from "../components/BoundingBoxOverlay.jsx";

export default function DetectionScreen({ result, onNext }) {
  if (!result) return null;
  const { vehicle_type, violation_label, confidence, boxes, annotated_image_url } = result;

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 grid md:grid-cols-2 gap-8">
      <div>
        <p className="eyebrow mb-2">Screen 02 — Detection Result</p>
        <h1 className="font-display text-3xl font-semibold mb-6">
          Vehicle &amp; Violation Detected
        </h1>
        <BoundingBoxOverlay src={annotated_image_url} boxes={boxes} alt="Detection result" />
      </div>

      <div className="flex flex-col gap-4">
        <Card className="flex flex-col gap-5">
          <DataRow label="Vehicle" value={vehicle_type} />
          <DataRow label="Violation" value={violation_label} accent />
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-textmuted block mb-1">
              Confidence
            </span>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2 rounded-full bg-border overflow-hidden">
                <div
                  className="h-full bg-cyan rounded-full"
                  style={{ width: `${confidence * 100}%` }}
                />
              </div>
              <span className="font-mono text-cyan text-lg">{(confidence * 100).toFixed(0)}%</span>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Badge tone="cyan">{boxes.filter((b) => b.kind === "detection").length} raw detections</Badge>
            <Badge tone="amber">{boxes.filter((b) => b.kind !== "detection").length} flagged region(s)</Badge>
          </div>
        </Card>

        <button
          onClick={onNext}
          className="mt-2 self-start bg-cyan text-base font-mono font-medium px-6 py-3 rounded-lg hover:opacity-90 transition-opacity"
        >
          Read Number Plate →
        </button>
      </div>
    </div>
  );
}
