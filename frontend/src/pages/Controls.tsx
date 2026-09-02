import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { ControlAssessment, ControlGapFinding } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

const EFFECTIVENESS_OPTIONS = ["not_assessed", "effective", "partially_effective", "ineffective"];

const STATUS_CLASS: Record<string, string> = {
  Effective: "badge-low",
  "Partially Effective": "badge-moderate",
  Ineffective: "badge-critical",
  "Not Assessed": "badge-moderate",
};

export default function Controls() {
  const [assessments, setAssessments] = useState<ControlAssessment[]>([]);
  const [findings, setFindings] = useState<ControlGapFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([
      apiClient.get<ControlAssessment[]>("/controls/assessments"),
      apiClient.get<ControlGapFinding[]>("/controls/gap-analysis"),
    ])
      .then(([assessmentsRes, findingsRes]) => {
        setAssessments(assessmentsRes.data);
        setFindings(findingsRes.data);
      })
      .catch(() => setError("Could not load control data."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  async function updateEffectiveness(
    assessmentId: number,
    field: "design_effectiveness" | "operating_effectiveness",
    value: string
  ) {
    await apiClient.patch(`/controls/assessments/${assessmentId}`, {
      [field]: value,
      reason: `Updated ${field.replace("_", " ")} via Control Assessment page.`,
    });
    load();
  }

  return (
    <div>
      <h1 className="page-title">Control Assessment</h1>
      <p className="page-subtitle">
        Risk → Control → Objective → Framework Reference → Evidence → Testing → Status. Design and
        operating effectiveness are tracked separately — a control isn't "working" just because it's
        well designed.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Gap Analysis ({findings.length})</h2>
          {findings.map((f, i) => (
            <div className="card" key={i} style={{ marginBottom: 8, display: "flex", justifyContent: "space-between" }}>
              <div style={{ fontSize: 13 }}>
                <strong>{f.control_id}</strong> — {f.detail}
              </div>
              <SeverityBadge band={f.severity} />
            </div>
          ))}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Control Assessments</h2>
          {assessments.map((a) => {
            const isOpen = expanded === a.id;
            return (
              <div className="card" key={a.id} style={{ marginBottom: 14 }}>
                <div
                  style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }}
                  onClick={() => setExpanded(isOpen ? null : a.id)}
                >
                  <div>
                    <strong>
                      {a.control.control_id} — {a.control.title}
                    </strong>
                    <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                      {a.control.framework_reference}
                    </div>
                  </div>
                  <span className={`badge ${STATUS_CLASS[a.overall_status] ?? "badge-moderate"}`}>
                    {a.overall_status}
                  </span>
                </div>

                {isOpen && (
                  <div style={{ marginTop: 14 }}>
                    <p style={{ fontSize: 13 }}>{a.control.description}</p>
                    <div style={{ fontSize: 13, marginBottom: 10 }}>
                      <strong>Objective: </strong>
                      {a.control.control_objective}
                    </div>
                    <div style={{ fontSize: 13, marginBottom: 10 }}>
                      <strong>Test procedure: </strong>
                      {a.control.test_procedure}
                    </div>

                    <div style={{ display: "flex", gap: 20, marginBottom: 12 }}>
                      <div className="field" style={{ flex: 1 }}>
                        <label>Design effectiveness</label>
                        <select
                          value={a.design_effectiveness}
                          onChange={(e) => updateEffectiveness(a.id, "design_effectiveness", e.target.value)}
                        >
                          {EFFECTIVENESS_OPTIONS.map((o) => (
                            <option key={o} value={o}>
                              {o.replace(/_/g, " ")}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="field" style={{ flex: 1 }}>
                        <label>Operating effectiveness</label>
                        <select
                          value={a.operating_effectiveness}
                          onChange={(e) =>
                            updateEffectiveness(a.id, "operating_effectiveness", e.target.value)
                          }
                        >
                          {EFFECTIVENESS_OPTIONS.map((o) => (
                            <option key={o} value={o}>
                              {o.replace(/_/g, " ")}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {a.notes && (
                      <div style={{ fontSize: 13, background: "var(--bg)", padding: "8px 10px", borderRadius: 6, marginBottom: 10 }}>
                        {a.notes}
                      </div>
                    )}

                    <strong style={{ fontSize: 13 }}>Evidence ({a.evidence.length})</strong>
                    <table>
                      <thead>
                        <tr>
                          <th>Type</th>
                          <th>Source</th>
                          <th>Collected</th>
                          <th>Valid Until</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {a.evidence.map((e) => (
                          <tr key={e.id}>
                            <td>{e.evidence_type}</td>
                            <td>{e.source}</td>
                            <td>{e.collected_at}</td>
                            <td>{e.valid_until ?? "—"}</td>
                            <td>{e.status}</td>
                          </tr>
                        ))}
                        {a.evidence.length === 0 && (
                          <tr>
                            <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                              No evidence on file.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}
