import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Asset, ContinuityFinding, ContinuityPlan } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

export default function BusinessContinuity() {
  const [plans, setPlans] = useState<ContinuityPlan[]>([]);
  const [findings, setFindings] = useState<ContinuityFinding[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiClient.get<ContinuityPlan[]>("/business-continuity/plans"),
      apiClient.get<ContinuityFinding[]>("/business-continuity/findings"),
      apiClient.get<Asset[]>("/assets"),
    ])
      .then(([plansRes, findingsRes, assetsRes]) => {
        setPlans(plansRes.data);
        setFindings(findingsRes.data);
        setAssets(assetsRes.data);
      })
      .catch(() => setError("Could not load business continuity data."))
      .finally(() => setLoading(false));
  }, []);

  const assetById = new Map(assets.map((a) => [a.id, a]));

  return (
    <div>
      <h1 className="page-title">Business Continuity &amp; Disaster Recovery</h1>
      <p className="page-subtitle">
        RTO/RPO, backup and DR test currency, and recovery dependencies for critical systems.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Findings</h2>
          {findings.map((f, i) => (
            <div className="card" key={i} style={{ marginBottom: 8, display: "flex", justifyContent: "space-between" }}>
              <div style={{ fontSize: 13 }}>{f.detail}</div>
              <SeverityBadge band={f.severity} />
            </div>
          ))}
          {findings.length === 0 && <div className="card">No continuity findings.</div>}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Continuity Plans</h2>
          <div className="card" style={{ padding: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>RTO</th>
                  <th>RPO</th>
                  <th>Backup Frequency</th>
                  <th>Last Backup Test</th>
                  <th>Last DR Test</th>
                </tr>
              </thead>
              <tbody>
                {plans.map((p) => {
                  const asset = assetById.get(p.asset_id);
                  return (
                    <tr key={p.id}>
                      <td>{asset ? `${asset.asset_tag} — ${asset.name}` : p.asset_id}</td>
                      <td>{p.rto_hours !== null ? `${p.rto_hours}h` : "—"}</td>
                      <td>{p.rpo_hours !== null ? `${p.rpo_hours}h` : "—"}</td>
                      <td>{p.backup_frequency || "—"}</td>
                      <td>{p.last_backup_tested_at ?? "Never"}</td>
                      <td>{p.last_dr_test_at ?? "Never"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
