import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Asset, Criticality } from "../api/types";
import CriticalityBadge from "../components/CriticalityBadge";

const CRITICALITY_OPTIONS: Criticality[] = ["critical", "high", "medium", "low"];

export default function Assets() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [criticality, setCriticality] = useState<string>("");
  const [selected, setSelected] = useState<Asset | null>(null);

  useEffect(() => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (criticality) params.criticality = criticality;

    apiClient
      .get<Asset[]>("/assets", { params })
      .then((res) => {
        setAssets(res.data);
        setError(null);
      })
      .catch(() => setError("Could not load assets. You may not have permission, or the API is unreachable."))
      .finally(() => setLoading(false));
  }, [search, criticality]);

  return (
    <div>
      <h1 className="page-title">Asset Inventory</h1>
      <p className="page-subtitle">
        Northstar Financial Services enterprise asset register. Every downstream module (risk,
        vulnerabilities, IAM, controls) references an asset from here rather than duplicating ownership
        and criticality data.
      </p>

      <div className="card" style={{ marginBottom: 20, display: "flex", gap: 16 }}>
        <input
          placeholder="Search by name, tag, or owner..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ flex: 1, padding: 8, border: "1px solid var(--border)", borderRadius: 6 }}
        />
        <select
          value={criticality}
          onChange={(e) => setCriticality(e.target.value)}
          style={{ padding: 8, border: "1px solid var(--border)", borderRadius: 6 }}
        >
          <option value="">All criticalities</option>
          {CRITICALITY_OPTIONS.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading assets...</div>}

      {!loading && !error && (
        <div className="card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Tag</th>
                <th>Name</th>
                <th>Type</th>
                <th>Business Unit</th>
                <th>Environment</th>
                <th>Criticality</th>
                <th>Internet Exposed</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id} onClick={() => setSelected(asset)} style={{ cursor: "pointer" }}>
                  <td>{asset.asset_tag}</td>
                  <td>{asset.name}</td>
                  <td>{asset.asset_type}</td>
                  <td>{asset.business_unit}</td>
                  <td>{asset.environment}</td>
                  <td>
                    <CriticalityBadge value={asset.criticality} />
                  </td>
                  <td>{asset.internet_exposed ? "Yes" : "No"}</td>
                </tr>
              ))}
              {assets.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                    No assets match the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {selected && (
        <div className="card" style={{ marginTop: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ margin: 0, fontSize: 16 }}>
              {selected.asset_tag} — {selected.name}
            </h2>
            <button className="btn-primary" style={{ width: "auto", padding: "6px 14px" }} onClick={() => setSelected(null)}>
              Close
            </button>
          </div>
          <table style={{ marginTop: 12 }}>
            <tbody>
              <tr><th>Owner</th><td>{selected.owner}</td></tr>
              <tr><th>Business Unit</th><td>{selected.business_unit}</td></tr>
              <tr><th>Technology</th><td>{selected.technology}</td></tr>
              <tr><th>Authentication</th><td>{selected.authentication_method}</td></tr>
              <tr><th>Data Classification</th><td>{selected.data_classification}</td></tr>
              <tr><th>Encrypted</th><td>{selected.encrypted ? "Yes" : "No"}</td></tr>
              <tr><th>Logging Enabled</th><td>{selected.logging_enabled ? "Yes" : "No"}</td></tr>
              <tr><th>Backup Enabled</th><td>{selected.backup_enabled ? "Yes" : "No"}</td></tr>
              <tr><th>Notes</th><td>{selected.notes || "-"}</td></tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
