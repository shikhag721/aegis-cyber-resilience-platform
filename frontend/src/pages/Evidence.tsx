import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { ControlAssessment, EvidenceItem } from "../api/types";

const STATUS_CLASS: Record<string, string> = {
  valid: "badge-low",
  pending_review: "badge-moderate",
  expired: "badge-critical",
};

export default function Evidence() {
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [assessments, setAssessments] = useState<ControlAssessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiClient.get<EvidenceItem[]>("/evidence"),
      apiClient.get<ControlAssessment[]>("/controls/assessments"),
    ])
      .then(([evidenceRes, assessmentsRes]) => {
        setEvidence(evidenceRes.data);
        setAssessments(assessmentsRes.data);
      })
      .catch(() => setError("Could not load the evidence register."))
      .finally(() => setLoading(false));
  }, []);

  const assessmentById = new Map(assessments.map((a) => [a.id, a]));

  return (
    <div>
      <h1 className="page-title">Evidence Register</h1>
      <p className="page-subtitle">
        Every piece of evidence supporting a control's effectiveness rating, across all controls.
        Governance is evidence-based: an effectiveness claim with no evidence here is a gap-analysis
        finding in its own right.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <div className="card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Control</th>
                <th>Evidence Type</th>
                <th>Source</th>
                <th>Collected</th>
                <th>Valid Until</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((e) => {
                const assessment = assessmentById.get(e.control_assessment_id);
                return (
                  <tr key={e.id}>
                    <td>{assessment ? `${assessment.control.control_id} — ${assessment.control.title}` : "—"}</td>
                    <td>{e.evidence_type}</td>
                    <td>{e.source}</td>
                    <td>{e.collected_at}</td>
                    <td>{e.valid_until ?? "—"}</td>
                    <td>
                      <span className={`badge ${STATUS_CLASS[e.status] ?? "badge-moderate"}`}>
                        {e.status.replace(/_/g, " ")}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {evidence.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                    No evidence recorded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
