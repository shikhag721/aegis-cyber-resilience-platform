import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Asset, RiskRecord, Vulnerability } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";
import ScoreBadge from "../components/ScoreBadge";

export default function Vulnerabilities() {
  const [vulns, setVulns] = useState<Vulnerability[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [riskById, setRiskById] = useState<Map<number, RiskRecord>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([
      apiClient.get<Vulnerability[]>("/vulnerabilities"),
      apiClient.get<Asset[]>("/assets"),
      apiClient.get<RiskRecord[]>("/risk-register"),
    ])
      .then(([vulnRes, assetRes, riskRes]) => {
        setVulns(vulnRes.data);
        setAssets(assetRes.data);
        setRiskById(new Map(riskRes.data.map((r) => [r.id, r])));
        setError(null);
      })
      .catch(() => setError("Could not load vulnerabilities."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const assetById = new Map(assets.map((a) => [a.id, a]));

  async function handleAssess(vulnId: number) {
    setBusyId(vulnId);
    try {
      await apiClient.post(`/vulnerabilities/${vulnId}/assess`, { control_effectiveness: 0.2 });
      load();
    } catch {
      setError("Could not run the business-risk assessment.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div>
      <h1 className="page-title">Vulnerability Management</h1>
      <p className="page-subtitle">
        Technical severity (CVSS) is tracked separately from business risk. Click "Assess Business Risk"
        to run a finding through the shared risk engine using the affected asset's actual context —
        criticality, exposure, and data sensitivity, not just the CVSS number.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <div className="card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>CVE</th>
                <th>Title</th>
                <th>Asset</th>
                <th>CVSS</th>
                <th>Known Exploited</th>
                <th>Status</th>
                <th>Business Risk (residual)</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {vulns.map((v) => {
                const asset = assetById.get(v.asset_id);
                const risk = v.risk_record_id ? riskById.get(v.risk_record_id) : undefined;
                return (
                  <tr key={v.id}>
                    <td>{v.cve_id ?? "—"}</td>
                    <td>{v.title}</td>
                    <td>{asset ? `${asset.asset_tag} (${asset.criticality})` : v.asset_id}</td>
                    <td>
                      {v.cvss_score.toFixed(1)} <SeverityBadge band={v.cvss_severity_band} />
                    </td>
                    <td>{v.known_exploited ? "Yes" : "No"}</td>
                    <td>{v.remediation_status.replace(/_/g, " ")}</td>
                    <td>{risk ? <ScoreBadge score={risk.residual_score} /> : "Not assessed"}</td>
                    <td>
                      {!v.risk_record_id && (
                        <button
                          className="btn-primary"
                          style={{ width: "auto", padding: "4px 10px", fontSize: 12 }}
                          disabled={busyId === v.id}
                          onClick={() => handleAssess(v.id)}
                        >
                          {busyId === v.id ? "Assessing..." : "Assess Business Risk"}
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="card" style={{ marginTop: 20, fontSize: 13 }}>
        <strong>Why this matters (Section 9):</strong> notice that a CVSS 10.0, known-exploited finding
        can score a <em>lower</em> business risk than a CVSS 8.8 finding, if the CVSS-10 asset is
        isolated and low-value while the CVSS-8.8 asset is internet-facing and holds sensitive data.
        CVSS measures technical severity; the Risk Register measures business risk. They are not the
        same number.
      </div>
    </div>
  );
}
