import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { AISystem } from "../api/types";

function GovernanceFlag({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      style={{
        fontSize: 11,
        padding: "2px 8px",
        borderRadius: 10,
        marginRight: 6,
        background: ok ? "var(--bg)" : "var(--critical-bg, #fdecea)",
        color: ok ? "var(--text-muted)" : "var(--critical)",
        border: `1px solid ${ok ? "var(--border)" : "var(--critical)"}`,
      }}
    >
      {ok ? "✓" : "✕"} {label}
    </span>
  );
}

export default function AIInventory() {
  const [systems, setSystems] = useState<AISystem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<AISystem[]>("/ai-inventory")
      .then((res) => setSystems(res.data))
      .catch(() => setError("Could not load the AI system inventory."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="page-title">AI Inventory</h1>
      <p className="page-subtitle">
        Every known AI system in use across Northstar Financial Services — model provider, data
        processed, tool access, and human oversight — the foundation the AI Security gap analysis
        runs against.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          {systems.map((s) => (
            <div className="card" key={s.id} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <strong>{s.name}</strong>
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  {s.deployment_environment} · {s.regulatory_risk_tier} regulatory tier
                </span>
              </div>
              <p style={{ fontSize: 13, margin: "6px 0" }}>{s.purpose}</p>
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 8 }}>
                Model provider: {s.model_provider} · Owner: {s.business_owner} ({s.technical_owner})
              </div>
              <div style={{ fontSize: 12, marginBottom: 8 }}>
                Data processed: {s.data_processed}
                <br />
                User base: {s.user_base}
              </div>
              {s.tools_available.length > 0 && (
                <div style={{ fontSize: 12, marginBottom: 8 }}>
                  Tools available: {s.tools_available.join(", ")}
                </div>
              )}
              {s.integrations.length > 0 && (
                <div style={{ fontSize: 12, marginBottom: 8 }}>
                  Integrations: {s.integrations.join(", ")}
                </div>
              )}
              <div>
                <GovernanceFlag ok={s.human_oversight} label="Human oversight" />
                <GovernanceFlag ok={s.monitoring_enabled} label="Monitoring enabled" />
                <GovernanceFlag ok={!s.influences_decisions} label="No unreviewed decision influence" />
              </div>
              {s.findings.length > 0 && (
                <div style={{ fontSize: 12, marginTop: 8, color: "var(--text-muted)" }}>
                  {s.findings.length} security finding(s) — see AI Security.
                </div>
              )}
            </div>
          ))}
          {systems.length === 0 && <div className="card">No AI systems recorded.</div>}
        </>
      )}
    </div>
  );
}
