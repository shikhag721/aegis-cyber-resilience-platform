import { FormEvent, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Asset, RiskRecord } from "../api/types";
import ScoreBadge from "../components/ScoreBadge";

const SEVERITY_OPTIONS = ["low", "medium", "high", "critical"];

export default function RiskRegister() {
  const [records, setRecords] = useState<RiskRecord[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assetId, setAssetId] = useState<number | "">("");
  const [severity, setSeverity] = useState("medium");
  const [knownExploited, setKnownExploited] = useState(false);
  const [controlEffectiveness, setControlEffectiveness] = useState(0);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([apiClient.get<RiskRecord[]>("/risk-register"), apiClient.get<Asset[]>("/assets")])
      .then(([riskRes, assetRes]) => {
        setRecords(riskRes.data);
        setAssets(assetRes.data);
        setError(null);
      })
      .catch(() => setError("Could not load the risk register."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const assetById = new Map(assets.map((a) => [a.id, a]));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    if (!assetId) {
      setSubmitError("Select an asset.");
      return;
    }
    try {
      await apiClient.post("/risk-register", {
        title,
        description,
        asset_id: assetId,
        threat_severity: severity,
        known_exploited: knownExploited,
        control_effectiveness: controlEffectiveness,
      });
      setTitle("");
      setDescription("");
      setAssetId("");
      setSeverity("medium");
      setKnownExploited(false);
      setControlEffectiveness(0);
      setShowForm(false);
      load();
    } catch {
      setSubmitError("Could not create the risk record. Check required fields and your permissions.");
    }
  }

  return (
    <div>
      <h1 className="page-title">Risk Register</h1>
      <p className="page-subtitle">
        Every entry here comes from the dedicated risk engine (likelihood × impact, asset criticality,
        exposure, control effectiveness) — never an LLM-assigned number. Sorted by residual score,
        highest first.
      </p>

      <button
        className="btn-primary"
        style={{ width: "auto", padding: "8px 16px", marginBottom: 16 }}
        onClick={() => setShowForm(!showForm)}
      >
        {showForm ? "Cancel" : "+ New Risk Assessment"}
      </button>

      {showForm && (
        <form className="card" style={{ marginBottom: 20 }} onSubmit={handleSubmit}>
          {submitError && <div className="error-text">{submitError}</div>}
          <div className="field">
            <label>Title</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="field">
            <label>Description</label>
            <input value={description} onChange={(e) => setDescription(e.target.value)} required />
          </div>
          <div className="field">
            <label>Asset</label>
            <select
              value={assetId}
              onChange={(e) => setAssetId(e.target.value ? Number(e.target.value) : "")}
              required
            >
              <option value="">Select an asset...</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.asset_tag} — {a.name} ({a.criticality})
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Threat / vulnerability severity</label>
            <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
              {SEVERITY_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>
              <input
                type="checkbox"
                checked={knownExploited}
                onChange={(e) => setKnownExploited(e.target.checked)}
              />{" "}
              Known exploited (e.g. CISA KEV)
            </label>
          </div>
          <div className="field">
            <label>Control effectiveness (0.0 = none, 1.0 = fully effective): {controlEffectiveness}</label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.1}
              value={controlEffectiveness}
              onChange={(e) => setControlEffectiveness(Number(e.target.value))}
            />
          </div>
          <button className="btn-primary" type="submit">
            Run Risk Assessment
          </button>
        </form>
      )}

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading &&
        !error &&
        records.map((record) => {
          const asset = assetById.get(record.asset_id);
          const isOpen = expanded === record.id;
          return (
            <div className="card" key={record.id} style={{ marginBottom: 14 }}>
              <div
                style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }}
                onClick={() => setExpanded(isOpen ? null : record.id)}
              >
                <div>
                  <strong>{record.title}</strong>
                  <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
                    {asset ? `${asset.asset_tag} — ${asset.name}` : `Asset #${record.asset_id}`} · status:{" "}
                    {record.status.replace(/_/g, " ")}
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <ScoreBadge score={record.residual_score} />
                  <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                    inherent {record.inherent_score} → residual {record.residual_score}
                  </div>
                </div>
              </div>

              {isOpen && (
                <div style={{ marginTop: 14 }}>
                  <p style={{ fontSize: 13 }}>{record.description}</p>

                  <div style={{ fontSize: 13, marginBottom: 10 }}>
                    <strong>Contributing factors:</strong>
                    <ul style={{ marginTop: 6 }}>
                      {record.contributing_factors.map((f, i) => (
                        <li key={i}>
                          {f.name} ({f.axis}, weight {f.weight}) — {f.reason}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div style={{ fontSize: 13, background: "var(--bg)", padding: "8px 10px", borderRadius: 6, marginBottom: 8 }}>
                    <strong>Primary concern: </strong>
                    {record.primary_concern}
                  </div>
                  <div style={{ fontSize: 13, background: "var(--bg)", padding: "8px 10px", borderRadius: 6 }}>
                    <strong>Recommended treatment (suggestion only): </strong>
                    {record.recommended_treatment}
                  </div>

                  {record.treatment_decision ? (
                    <div style={{ fontSize: 13, marginTop: 10 }}>
                      <strong>Recorded decision:</strong> {record.treatment_decision} — owned by{" "}
                      {record.owner}. {record.treatment_reason}
                    </div>
                  ) : (
                    <div style={{ fontSize: 13, marginTop: 10, color: "var(--text-muted)" }}>
                      No treatment decision recorded yet.
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
