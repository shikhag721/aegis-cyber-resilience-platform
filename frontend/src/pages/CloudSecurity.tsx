import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Asset, CloudFinding } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

export default function CloudSecurity() {
  const [findings, setFindings] = useState<CloudFinding[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([apiClient.get<CloudFinding[]>("/cloud/findings"), apiClient.get<Asset[]>("/assets")])
      .then(([findingsRes, assetRes]) => {
        setFindings(findingsRes.data);
        setAssets(assetRes.data);
      })
      .catch(() => setError("Could not load cloud security findings."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const assetById = new Map(assets.map((a) => [a.id, a]));

  async function markRemediated(id: number) {
    await apiClient.patch(`/cloud/findings/${id}/status`, null, { params: { status: "remediated" } });
    load();
  }

  return (
    <div>
      <h1 className="page-title">Cloud Security Posture</h1>
      <p className="page-subtitle">
        Structured cloud configuration findings — IAM permissions, storage exposure, network security
        groups, configuration drift, and exposed secrets. Modeled findings, not a live cloud API
        integration (see docs/architecture/limitations.md).
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading &&
        !error &&
        findings.map((f) => {
          const asset = f.asset_id ? assetById.get(f.asset_id) : undefined;
          return (
            <div className="card" key={f.id} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <div>
                  <strong>{f.resource_name}</strong>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                    {f.finding_type.replace(/_/g, " ")} {asset ? `· ${asset.asset_tag}` : ""} · status:{" "}
                    {f.status.replace(/_/g, " ")}
                  </div>
                </div>
                <SeverityBadge band={f.severity} />
              </div>
              <p style={{ fontSize: 13, margin: "8px 0" }}>{f.description}</p>
              <div style={{ fontSize: 13, background: "var(--bg)", padding: "8px 10px", borderRadius: 6 }}>
                <strong>Recommendation: </strong>
                {f.recommendation}
              </div>
              {f.status === "open" && (
                <button
                  className="btn-primary"
                  style={{ width: "auto", padding: "5px 12px", fontSize: 12, marginTop: 10 }}
                  onClick={() => markRemediated(f.id)}
                >
                  Mark Remediated
                </button>
              )}
            </div>
          );
        })}
    </div>
  );
}
