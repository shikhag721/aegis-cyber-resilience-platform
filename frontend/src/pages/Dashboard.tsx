import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiClient } from "../api/client";
import { ExecutiveSummary } from "../api/types";

function MetricCard({
  label,
  value,
  tone,
  to,
}: {
  label: string;
  value: number | string;
  tone?: "critical" | "high" | "ok";
  to?: string;
}) {
  const color =
    tone === "critical" ? "var(--critical)" : tone === "high" ? "var(--high)" : "var(--text)";
  const content = (
    <div className="card">
      <div className="metric-label">{label}</div>
      <div className="metric-value" style={{ color }}>
        {value}
      </div>
    </div>
  );
  return to ? (
    <Link to={to} style={{ textDecoration: "none", color: "inherit" }}>
      {content}
    </Link>
  ) : (
    content
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<ExecutiveSummary>("/dashboard/summary")
      .then((res) => setSummary(res.data))
      .catch(() => setError("Could not load dashboard summary."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="page-title">Executive Dashboard</h1>
      <p className="page-subtitle">
        Northstar Financial Services - live security posture, aggregated from every domain module. Every
        number here is either a stored field or the output of an existing deterministic analyzer - see{" "}
        <Link to="/reports">Reports</Link> for the full narrative summary.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && summary && (
        <>
          <h2 style={{ fontSize: 15, margin: "0 0 10px" }}>Risk &amp; Vulnerability</h2>
          <div className="card-grid">
            <MetricCard
              label="Open Risks (Critical)"
              value={summary.risks_by_residual_rating["Critical"] ?? 0}
              tone="critical"
              to="/risk-register"
            />
            <MetricCard
              label="Open Risks (Total)"
              value={summary.risks_open}
              to="/risk-register"
            />
            <MetricCard
              label="Known-Exploited Vulns (Open)"
              value={summary.vulnerabilities_known_exploited_open}
              tone={summary.vulnerabilities_known_exploited_open > 0 ? "critical" : "ok"}
              to="/vulnerabilities"
            />
            <MetricCard
              label="Overdue Remediation"
              value={summary.vulnerabilities_overdue}
              tone={summary.vulnerabilities_overdue > 0 ? "high" : "ok"}
              to="/vulnerabilities"
            />
          </div>

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Governance &amp; Response</h2>
          <div className="card-grid">
            <MetricCard
              label="Ineffective Controls"
              value={summary.control_gaps_critical}
              tone={summary.control_gaps_critical > 0 ? "critical" : "ok"}
              to="/controls"
            />
            <MetricCard label="Control Gaps (Total)" value={summary.control_gaps_total} to="/controls" />
            <MetricCard
              label="Open Incidents (High/Critical)"
              value={summary.incidents_open_high_or_critical}
              tone={summary.incidents_open_high_or_critical > 0 ? "critical" : "ok"}
              to="/incidents"
            />
            <MetricCard
              label="Vendors High/Critical Risk"
              value={summary.vendors_high_or_critical}
              tone={summary.vendors_high_or_critical > 0 ? "high" : "ok"}
              to="/vendors"
            />
          </div>

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>AI Security</h2>
          <div className="card-grid">
            <MetricCard
              label="AI Governance Gaps (Critical)"
              value={summary.ai_governance_gaps_critical}
              tone={summary.ai_governance_gaps_critical > 0 ? "critical" : "ok"}
              to="/ai-security"
            />
            <MetricCard label="RAG Findings" value={summary.rag_findings} to="/rag-security" />
            <MetricCard
              label="Agents High/Critical Blast Radius"
              value={summary.agents_high_or_critical}
              tone={summary.agents_high_or_critical > 0 ? "high" : "ok"}
              to="/agent-security"
            />
          </div>

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Environment</h2>
          <div className="card-grid">
            <MetricCard label="Assets Tracked" value={summary.assets_total} to="/assets" />
            <MetricCard
              label="Critical Assets"
              value={summary.assets_by_criticality["critical"] ?? 0}
              to="/assets"
            />
            <MetricCard label="IAM Findings" value={summary.iam_findings_total} to="/iam" />
            <MetricCard label="Open Secrets Findings" value={summary.secrets_open} to="/app-security" />
          </div>
        </>
      )}
    </div>
  );
}
