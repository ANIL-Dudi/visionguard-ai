import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";

export default function PlateScreen({ result, onNext }) {
  if (!result) return null;
  const { plate } = result;
  const hasPlate = Boolean(plate.text);

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <p className="eyebrow mb-2">Screen 03 — Number Plate</p>
      <h1 className="font-display text-3xl font-semibold mb-6">
        Plate Recognition (ANPR)
      </h1>

      <Card className="flex flex-col items-center gap-6 py-12">
        {hasPlate ? (
          <>
            <div className="bg-textprimary text-base px-8 py-4 rounded-md border-4 border-base">
              <span className="font-mono text-4xl font-bold tracking-wider text-base">
                {plate.text}
              </span>
            </div>
            <div className="flex gap-3">
              <Badge tone="cyan">OCR confidence {(plate.confidence * 100).toFixed(0)}%</Badge>
              <Badge tone={plate.valid_format ? "cyan" : "amber"}>
                {plate.valid_format ? "Valid format" : "Format unverified"}
              </Badge>
            </div>
          </>
        ) : (
          <>
            <div className="bg-panel2 text-textmuted px-8 py-4 rounded-md border-2 border-dashed border-border">
              <span className="font-mono text-2xl tracking-wider">UNREADABLE</span>
            </div>
            <Badge tone="amber">Plate not confidently localized — manual review suggested</Badge>
          </>
        )}
      </Card>

      <button
        onClick={onNext}
        className="mt-6 bg-cyan text-base font-mono font-medium px-6 py-3 rounded-lg hover:opacity-90 transition-opacity"
      >
        Generate Evidence →
      </button>
    </div>
  );
}
