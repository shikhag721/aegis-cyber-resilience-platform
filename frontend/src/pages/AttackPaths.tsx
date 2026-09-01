import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { AttackPath, Asset } from "../api/types";
import ScoreBadge from "../components/ScoreBadge";

export default function AttackPaths() {
  const [paths, setPaths] = useState<AttackPath[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([apiClient.get<AttackPath[]>("/attack-paths"), apiClient.get<Asset[]>("/assets")])
      .then(([pathsRes, assetsRes]) => {
        setPaths(pathsRes.data);
        setAssets(assetsRes.data);
      })
      .catch(() => setError("Could not load attack paths."))
      .finally(() => setLoading(false));
  }, []);

  const assetById = new Map(assets.map((a) => [a.id, a]));

  return (
    <div>
      <h1 className="page-title">Attack Paths</h1>
      <p className="page-subtitle">
        Concrete, asset-specific attack scenarios, ranked by likelihood × impact — highest first. Each
        path is a chain from an entry point through real Northstar assets to a target.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading &&
        !error &&
        paths.map((path) => {
          const target = assetById.get(path.target_asset_id);
          const isOpen = expanded === path.id;
          return (
            <div className="card" key={path.id} style={{ marginBottom: 14 }}>
              <div
                style={{ display: "flex", justifyContent: "space-between", cursor: "pointer" }}
                onClick={() => setExpanded(isOpen ? null : path.id)}
              >
                <div>
                  <strong>{path.name}</strong>
                  <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
                    {path.entry_point} → {target?.name ?? `Asset #${path.target_asset_id}`}
                  </div>
                </div>
                <ScoreBadge score={path.score} />
              </div>

              {isOpen && (
                <div style={{ marginTop: 14 }}>
                  <p style={{ fontSize: 13 }}>{path.description}</p>
                  <table>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Step</th>
                        <th>Asset</th>
                      </tr>
                    </thead>
                    <tbody>
                      {path.steps.map((step) => (
                        <tr key={step.id}>
                          <td>{step.sequence}</td>
                          <td>{step.description}</td>
                          <td>{step.asset_id ? assetById.get(step.asset_id)?.name ?? "-" : "-"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {path.notes && (
                    <div style={{ fontSize: 13, marginTop: 10, color: "var(--text-muted)" }}>
                      <strong>Notes: </strong>
                      {path.notes}
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
