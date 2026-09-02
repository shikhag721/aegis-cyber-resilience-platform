import { FormEvent, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { CorrelationFinding, Incident } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

const STAGE_LABELS: Record<string, string> = {
  detection: "Detection",
  triage: "Triage",
  investigation: "Investigation",
  containment: "Containment",
  eradication: "Eradication",
  recovery: "Recovery",
  lessons_learned: "Lessons Learned",
};

export default function Incidents() {
  const [findings, setFindings] = useState<CorrelationFinding[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [advanceNote, setAdvanceNote] = useState("");
  const [advanceError, setAdvanceError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([
      apiClient.get<CorrelationFinding[]>("/security-events/correlate"),
      apiClient.get<Incident[]>("/incidents"),
    ])
      .then(([findingsRes, incidentsRes]) => {
        setFindings(findingsRes.data);
        setIncidents(incidentsRes.data);
      })
      .catch(() => setError("Could not load incident response data."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  async function handleAdvance(e: FormEvent, incidentId: number) {
    e.preventDefault();
    setAdvanceError(null);
    try {
      await apiClient.post(`/incidents/${incidentId}/advance`, { description: advanceNote });
      setAdvanceNote("");
      load();
    } catch {
      setAdvanceError("Could not advance the incident — note must be at least 10 characters.");
    }
  }

  return (
    <div>
      <h1 className="page-title">Security Monitoring &amp; Incident Response</h1>
      <p className="page-subtitle">
        Correlated security-event findings (not a single alert, but a full plausible attack chain), and
        the incident lifecycle — Detection through Lessons Learned — for confirmed incidents.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Correlated Event Findings</h2>
          {findings.length === 0 && <div className="card">No correlated suspicious event chains detected.</div>}
          {findings.map((f, i) => (
            <div className="card" key={i} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{f.username}</strong>
                <SeverityBadge band={f.severity} />
              </div>
              <p style={{ fontSize: 13, margin: "6px 0" }}>{f.narrative}</p>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                Event sequence: {f.matched_event_types.join(" → ")}
              </div>
            </div>
          ))}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Incidents</h2>
          {incidents.map((incident) => {
            const isOpen = expanded === incident.id;
            const isFinal = incident.stage === "lessons_learned";
            return (
              <div className="card" key={incident.id} style={{ marginBottom: 14 }}>
                <div
                  style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }}
                  onClick={() => setExpanded(isOpen ? null : incident.id)}
                >
                  <div>
                    <strong>{incident.title}</strong>
                    <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                      Stage: {STAGE_LABELS[incident.stage] ?? incident.stage}
                    </div>
                  </div>
                  <SeverityBadge band={incident.severity} />
                </div>

                {isOpen && (
                  <div style={{ marginTop: 14 }}>
                    <p style={{ fontSize: 13 }}>{incident.description}</p>
                    <div style={{ fontSize: 13, background: "var(--bg)", padding: "8px 10px", borderRadius: 6, marginBottom: 10 }}>
                      <strong>Recommended containment: </strong>
                      {incident.recommended_containment || "—"}
                    </div>

                    <strong style={{ fontSize: 13 }}>Timeline</strong>
                    <table>
                      <thead>
                        <tr>
                          <th>Stage</th>
                          <th>Note</th>
                          <th>When</th>
                        </tr>
                      </thead>
                      <tbody>
                        {incident.timeline.map((t) => (
                          <tr key={t.id}>
                            <td>{STAGE_LABELS[t.stage] ?? t.stage}</td>
                            <td>{t.description}</td>
                            <td>{new Date(t.occurred_at).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    {!isFinal && (
                      <form onSubmit={(e) => handleAdvance(e, incident.id)} style={{ marginTop: 12 }}>
                        {advanceError && <div className="error-text">{advanceError}</div>}
                        <div className="field">
                          <label>Advance to next stage — add a note</label>
                          <input value={advanceNote} onChange={(e) => setAdvanceNote(e.target.value)} required />
                        </div>
                        <button className="btn-primary" style={{ width: "auto", padding: "6px 14px" }} type="submit">
                          Advance Stage
                        </button>
                      </form>
                    )}
                  </div>
                )}
              </div>
            );
          })}
          {incidents.length === 0 && <div className="card">No incidents recorded.</div>}
        </>
      )}
    </div>
  );
}
