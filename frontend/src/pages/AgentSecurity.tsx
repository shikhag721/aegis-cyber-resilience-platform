import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { AgentAssessment, AIAgent } from "../api/types";
import ScoreBadge from "../components/ScoreBadge";

export default function AgentSecurity() {
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [assessments, setAssessments] = useState<Map<number, AgentAssessment>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    apiClient
      .get<AIAgent[]>("/agent-security/agents")
      .then(async (res) => {
        setAgents(res.data);
        const entries = await Promise.all(
          res.data.map(async (a) => {
            try {
              const assessment = await apiClient.get<AgentAssessment>(
                `/agent-security/agents/${a.id}/assessments/latest`
              );
              return [a.id, assessment.data] as const;
            } catch {
              return null;
            }
          })
        );
        setAssessments(new Map(entries.filter((e): e is [number, AgentAssessment] => e !== null)));
      })
      .catch(() => setError("Could not load AI agent data."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  async function runAssessment(agentId: number) {
    await apiClient.post(`/agent-security/agents/${agentId}/assessments`);
    load();
  }

  return (
    <div>
      <h1 className="page-title">AI Agent Security</h1>
      <p className="page-subtitle">
        Blast-radius assessment for AI agents that can take action, not just produce text — its own
        explainable scorer (ADR 0009) built from autonomy level, human-approval requirements,
        reversibility, financial capability, and guardrails.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading &&
        !error &&
        agents.map((a) => {
          const assessment = assessments.get(a.id);
          const isOpen = expanded === a.id;
          return (
            <div className="card" key={a.id} style={{ marginBottom: 14 }}>
              <div
                style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }}
                onClick={() => setExpanded(isOpen ? null : a.id)}
              >
                <div>
                  <strong>{a.name}</strong>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                    {a.purpose}
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
                      runAssessment(a.id);
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
                      <tr><th>Autonomy Level</th><td>{a.autonomy_level.replace(/_/g, " ")}</td></tr>
                      <tr><th>Tools Available</th><td>{a.tools_available.join(", ") || "None"}</td></tr>
                      <tr><th>Can Take Irreversible Actions</th><td>{a.can_take_irreversible_actions ? "Yes" : "No"}</td></tr>
                      <tr><th>Can Initiate Financial Transactions</th><td>{a.can_initiate_financial_transactions ? "Yes" : "No"}</td></tr>
                      <tr><th>Requires Human Approval</th><td>{a.requires_human_approval ? "Yes" : "No"}</td></tr>
                      <tr><th>Data Access Scope</th><td>{a.data_access_scope || "Not specified"}</td></tr>
                      <tr><th>Guardrails</th><td>{a.guardrails_description || "None documented"}</td></tr>
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
      {!loading && !error && agents.length === 0 && <div className="card">No AI agents recorded.</div>}
    </div>
  );
}
