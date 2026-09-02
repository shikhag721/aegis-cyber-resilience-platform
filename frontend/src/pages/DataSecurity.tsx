import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { DataAsset, DataSecurityFinding } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

export default function DataSecurity() {
  const [dataAssets, setDataAssets] = useState<DataAsset[]>([]);
  const [findings, setFindings] = useState<DataSecurityFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiClient.get<DataAsset[]>("/data-security/data-assets"),
      apiClient.get<DataSecurityFinding[]>("/data-security/findings"),
    ])
      .then(([assetsRes, findingsRes]) => {
        setDataAssets(assetsRes.data);
        setFindings(findingsRes.data);
      })
      .catch(() => setError("Could not load data security information."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="page-title">Data Security</h1>
      <p className="page-subtitle">
        Where specific sensitive data categories (PII, financial data, credentials, secrets) actually
        live, independent of the general asset classification — one system can hold several data
        categories with different exposure profiles.
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
          {findings.length === 0 && <div className="card">No data security findings.</div>}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Data Asset Catalog</h2>
          <div className="card" style={{ padding: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Category</th>
                  <th>Classification</th>
                  <th>Encrypted</th>
                  <th>Access Controlled</th>
                  <th>Retention Defined</th>
                </tr>
              </thead>
              <tbody>
                {dataAssets.map((d) => (
                  <tr key={d.id}>
                    <td>{d.name}</td>
                    <td>{d.category.replace(/_/g, " ")}</td>
                    <td>{d.classification}</td>
                    <td>{d.encrypted ? "Yes" : "No"}</td>
                    <td>{d.access_controlled ? "Yes" : "No"}</td>
                    <td>{d.retention_defined ? `Yes (${d.retention_period_days ?? "?"} days)` : "No"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
