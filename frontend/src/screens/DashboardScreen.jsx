import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import { getAnalyticsSummary, listViolations } from "../api/client.js";

const TYPE_LABELS = {
  helmet_non_compliance: "Helmet",
  triple_riding: "Triple Riding",
  seatbelt_violation: "Seatbelt",
  wrong_side_driving: "Wrong Side",
  red_light_violation: "Red Light",
  stop_line_violation: "Stop Line",
  illegal_parking: "Illegal Parking",
};

const BAR_COLOR = "#2DD4BF";

export default function DashboardScreen({ onRestart }) {
  const [summary, setSummary] = useState(null);
  const [violations, setViolations] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([getAnalyticsSummary(), listViolations(10)])
      .then(([s, v]) => {
        setSummary(s);
        setViolations(v);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return <p className="text-center text-red font-mono py-12">{error}</p>;
  }
  if (!summary) {
    return <p className="text-center text-textmuted font-mono py-12 animate-pulse">Loading analytics…</p>;
  }

  const chartData = Object.entries(summary.by_type).map(([key, count]) => ({
    name: TYPE_LABELS[key] || key,
    count,
  }));

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="eyebrow mb-2">Screen 06 — Analytics Dashboard</p>
          <h1 className="font-display text-3xl font-semibold">Enforcement Overview</h1>
        </div>
        <button
          onClick={onRestart}
          className="font-mono text-sm border border-border px-4 py-2 rounded-lg text-textmuted hover:text-cyan hover:border-cyan transition-colors"
        >
          + New Upload
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Violations" value={summary.total_violations} />
        <StatCard label="Avg Risk Score" value={summary.avg_risk_score} />
        <StatCard label="Repeat Offenders" value={summary.repeat_offender_count} />
        <StatCard label="Plates Flagged" value={summary.plates_flagged} />
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card className="md:col-span-2">
          <p className="text-xs font-mono uppercase tracking-wider text-textmuted mb-4">
            Violations by Type
          </p>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363D" vertical={false} />
                <XAxis dataKey="name" stroke="#8B949E" fontSize={12} />
                <YAxis stroke="#8B949E" fontSize={12} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ background: "#161B22", border: "1px solid #30363D", borderRadius: 8 }}
                  labelStyle={{ color: "#E6EDF3" }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={BAR_COLOR} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <p className="text-xs font-mono uppercase tracking-wider text-textmuted mb-4">
            Violation Engine
          </p>
          <div className="flex flex-col gap-2">
            {summary.implemented_modules.map((m) => (
              <div key={m} className="flex items-center justify-between text-sm">
                <span className="text-textprimary">{m}</span>
                <Badge tone="cyan">live</Badge>
              </div>
            ))}
            {summary.architecture_modules.map((m) => (
              <div key={m} className="flex items-center justify-between text-sm">
                <span className="text-textmuted">{m}</span>
                <Badge tone="muted">architecture</Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card>
        <p className="text-xs font-mono uppercase tracking-wider text-textmuted mb-4">
          Recent Violations
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-textmuted font-mono text-xs uppercase border-b border-border">
                <th className="py-2 pr-4">ID</th>
                <th className="py-2 pr-4">Vehicle</th>
                <th className="py-2 pr-4">Violation</th>
                <th className="py-2 pr-4">Plate</th>
                <th className="py-2 pr-4">Risk</th>
                <th className="py-2">Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {violations.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-textmuted">
                    No violations logged yet.
                  </td>
                </tr>
              )}
              {violations.map((v) => (
                <tr key={v.id} className="border-b border-border/50">
                  <td className="py-3 pr-4 font-mono text-cyan">{v.id}</td>
                  <td className="py-3 pr-4">{v.vehicle_type}</td>
                  <td className="py-3 pr-4">{v.violation_label}</td>
                  <td className="py-3 pr-4 font-mono">{v.plate_text || "—"}</td>
                  <td className="py-3 pr-4">
                    <Badge tone={v.risk_score >= 50 ? "red" : v.risk_score >= 20 ? "amber" : "cyan"}>
                      {v.risk_score} · {v.risk_level}
                    </Badge>
                  </td>
                  <td className="py-3 text-textmuted">{v.recommendation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <Card className="py-5">
      <p className="text-xs font-mono uppercase tracking-wider text-textmuted mb-2">{label}</p>
      <p className="font-display text-3xl font-semibold text-textprimary">{value}</p>
    </Card>
  );
}
