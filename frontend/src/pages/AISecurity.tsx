import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { AIInventoryFinding, AISecurityFinding } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

export default function AISecurity() {
  const [findings, setFindings] = useState<AISecurityFinding[]>([]);
  const [gapFindings, setGapFindings] = useState<AIInventoryFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiClient.get<AISecurityFinding[]>("/ai-security/findings"),
      apiClient.get<AIInventoryFinding[]>("/ai-security/gap-analysis"),
    ])
      .then(([findingsRes, gapRes]) => {
        setFindings(findingsRes.data);
        setGapFindings(gapRes.data);
      })
      .catch(() => setError("Could not load AI security data."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="page-title">AI Security</h1>
      <p className="page-subtitle">
        Analyst-identified findings against specific AI systems, plus a deterministic governance gap
        analysis computed live from the AI inventory (excessive agency, unreviewed decision influence,
        missing monitoring, high-tier third-party models without oversight).
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Governance Gap Analysis</h2>
          {gapFindings.map((f, i) => (
            <div
              className="card"
              key={i}
              style={{ marginBottom: 8, display: "flex", justifyContent: "space-between" }}
            >
              <div style={{ fontSize: 13 }}>
                <strong>{f.ai_system_name}</strong> — {f.detail}
              </div>
              <SeverityBadge band={f.severity} />
            </div>
          ))}
          {gapFindings.length === 0 && <div className="card">No governance gaps detected.</div>}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>AI Security Findings</h2>
          {findings.map((f) => (
            <div className="card" key={f.id} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{f.finding_type.replace(/_/g, " ")}</strong>
                <SeverityBadge band={f.severity} />
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)", margin: "4px 0" }}>
                Risk lens: {f.risk_lens} · Status: {f.status}
              </div>
              <p style={{ fontSize: 13 }}>{f.description}</p>
              <div style={{ fontSize: 13, background: "var(--bg)", padding: "6px 10px", borderRadius: 6 }}>
                <strong>Recommendation: </strong>
                {f.recommendation}
              </div>
            </div>
          ))}
          {findings.length === 0 && <div className="card">No AI security findings recorded.</div>}
        </>
      )}
    </div>
  );
}
