import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { ExecutiveReport, ReportHighlight } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

function HighlightList({ items, emptyText }: { items: ReportHighlight[]; emptyText: string }) {
  if (items.length === 0) return <div style={{ fontSize: 13, color: "var(--text-muted)" }}>{emptyText}</div>;
  return (
    <>
      {items.map((h, i) => (
        <div className="card" key={i} style={{ marginBottom: 8, display: "flex", justifyContent: "space-between" }}>
          <div style={{ fontSize: 13 }}>
            <strong>{h.title}</strong>
            <div style={{ color: "var(--text-muted)", marginTop: 2 }}>{h.detail}</div>
          </div>
          <SeverityBadge band={h.severity} />
        </div>
      ))}
    </>
  );
}

export default function Reports() {
  const [report, setReport] = useState<ExecutiveReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<ExecutiveReport>("/reports/executive-summary")
      .then((res) => setReport(res.data))
      .catch(() => setError("Could not load the executive report."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="print-hide" style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h1 className="page-title">Executive Report</h1>
        {report && (
          <button
            className="btn-primary"
            style={{ width: "auto", padding: "6px 14px", fontSize: 13 }}
            onClick={() => window.print()}
          >
            Print / Save as PDF
          </button>
        )}
      </div>
      <p className="page-subtitle print-hide">
        A point-in-time narrative summary of security posture, generated deterministically from the same
        data as the Dashboard - top risks, control gaps, and AI findings, plus threshold-based recommended
        actions. No LLM judgment involved; every line traces back to a stored field or an existing
        analyzer.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && report && (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <strong>Northstar Financial Services - Security Posture Report</strong>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
              Generated {new Date(report.generated_at).toLocaleString()}
            </div>
            <p style={{ fontSize: 13, marginTop: 10 }}>
              {report.summary.assets_total} assets tracked, {report.summary.risks_open} open risks (
              {report.summary.risks_by_residual_rating["Critical"] ?? 0} Critical),{" "}
              {report.summary.vulnerabilities_known_exploited_open} known-exploited vulnerabilities open,{" "}
              {report.summary.control_gaps_critical} controls assessed Ineffective, and{" "}
              {report.summary.ai_governance_gaps_critical} Critical AI governance gap(s).
            </p>
          </div>

          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Recommended Actions</h2>
          <ul style={{ marginBottom: 24 }}>
            {report.recommended_actions.map((a, i) => (
              <li key={i} style={{ fontSize: 13, marginBottom: 6 }}>
                {a}
              </li>
            ))}
          </ul>

          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Top Risks</h2>
          <div style={{ marginBottom: 24 }}>
            <HighlightList items={report.top_risks} emptyText="No open risks recorded." />
          </div>

          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Top Control Gaps</h2>
          <div style={{ marginBottom: 24 }}>
            <HighlightList items={report.top_control_gaps} emptyText="No control gaps identified." />
          </div>

          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Top AI Governance Findings</h2>
          <div style={{ marginBottom: 24 }}>
            <HighlightList items={report.top_ai_findings} emptyText="No AI governance gaps identified." />
          </div>
        </>
      )}
    </div>
  );
}
