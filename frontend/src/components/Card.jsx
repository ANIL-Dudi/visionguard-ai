export default function Card({ children, className = "" }) {
  return (
    <div className={`bg-panel border border-border rounded-xl p-6 ${className}`}>
      {children}
    </div>
  );
}

export function DataRow({ label, value, mono = true, accent = false }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs font-mono uppercase tracking-wider text-textmuted">
        {label}
      </span>
      <span
        className={`text-lg font-medium ${mono ? "font-mono" : "font-display"} ${
          accent ? "text-cyan" : "text-textprimary"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
