import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Vendor, VendorAssessmentResult } from "../api/types";
import ScoreBadge from "../components/ScoreBadge";

export default function Vendors() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [assessments, setAssessments] = useState<Map<number, VendorAssessmentResult>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    apiClient
      .get<Vendor[]>("/vendors")
      .then(async (res) => {
        setVendors(res.data);
        const entries = await Promise.all(
          res.data.map(async (v) => {
            try {
              const a = await apiClient.get<VendorAssessmentResult>(`/vendors/${v.id}/assessments/latest`);
              return [v.id, a.data] as const;
            } catch {
              return null;
            }
          })
        );
        setAssessments(new Map(entries.filter((e): e is [number, VendorAssessmentResult] => e !== null)));
      })
      .catch(() => setError("Could not load vendor data."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  async function runAssessment(vendorId: number) {
    await apiClient.post(`/vendors/${vendorId}/assessments`);
    load();
  }

  return (
    <div>
      <h1 className="page-title">Third-Party / Vendor Risk</h1>
      <p className="page-subtitle">
        Vendor risk uses its own explainable scorer (not a forced reuse of the asset risk engine — see
        ADR 0008) built from subprocessors, certifications, contract terms, and incident history.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading &&
        !error &&
        vendors.map((v) => {
          const assessment = assessments.get(v.id);
          const isOpen = expanded === v.id;
          return (
            <div className="card" key={v.id} style={{ marginBottom: 14 }}>
              <div
                style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }}
                onClick={() => setExpanded(isOpen ? null : v.id)}
              >
                <div>
                  <strong>{v.name}</strong>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                    {v.service_description}
                  </div>
                </div>
                {assessment ? (
                  <ScoreBadge score={assessment.score} />
                ) : (
                  <button
                    className="btn-primary"
                    style={{ width: "auto", padding: "5px 12px", fontSize: 12 }}
                    onClick={(e) => {
                      e.stopPropagation();
                      runAssessment(v.id);
                    }}
                  >
                    Run Assessment
                  </button>
                )}
              </div>

              {isOpen && (
                <div style={{ marginTop: 14, fontSize: 13 }}>
                  <table>
                    <tbody>
                      <tr><th>Business Criticality</th><td>{v.business_criticality}</td></tr>
                      <tr><th>Data Classification Handled</th><td>{v.data_classification_handled}</td></tr>
                      <tr><th>Certifications</th><td>{v.certifications || "None on file"}</td></tr>
                      <tr><th>Subprocessors</th><td>{v.subprocessors || "None disclosed"}</td></tr>
                      <tr><th>Incident History</th><td>{v.has_incident_history ? v.incident_history_notes : "None"}</td></tr>
                      <tr><th>Contractual Security Clause</th><td>{v.contractual_security_clause ? "Yes" : "No"}</td></tr>
                      <tr><th>Exit Strategy Defined</th><td>{v.exit_strategy_defined ? "Yes" : "No"}</td></tr>
                      <tr><th>Availability SLA</th><td>{v.availability_sla_percent ? `${v.availability_sla_percent}%` : "Not specified"}</td></tr>
                    </tbody>
                  </table>

                  {assessment && (
                    <div style={{ marginTop: 12 }}>
                      <strong>Contributing factors:</strong>
                      <ul>
                        {assessment.contributing_factors.map((f, i) => (
                          <li key={i}>
                            {f.name} ({f.axis}) — {f.reason}
                          </li>
                        ))}
                      </ul>
                      <div style={{ background: "var(--bg)", padding: "8px 10px", borderRadius: 6 }}>
                        <strong>Recommendation: </strong>
                        {assessment.recommendation}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
    </div>
  );
}
