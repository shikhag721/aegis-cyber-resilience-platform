import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { AuditLogEntry } from "../api/types";

export default function AuditLog() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<AuditLogEntry[]>("/audit-log")
      .then((res) => setEntries(res.data))
      .catch(() => setError("Could not load the audit log."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="page-title">Audit Log</h1>
      <p className="page-subtitle">
        Every governance-relevant state change — risk treatment decisions, control effectiveness
        changes, incident stage advances — recorded with the actor, old value, new value, and reason.
        Read-only: entries are only ever created as a side effect of the action itself.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <div className="card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>When</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Object</th>
                <th>Change</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.id}>
                  <td>{new Date(e.occurred_at).toLocaleString()}</td>
                  <td>{e.actor}</td>
                  <td>{e.action.replace(/_/g, " ")}</td>
                  <td>
                    {e.object_type} #{e.object_id}
                  </td>
                  <td style={{ fontFamily: "monospace", fontSize: 11 }}>
                    {JSON.stringify(e.old_value)} → {JSON.stringify(e.new_value)}
                  </td>
                  <td>{e.reason || "—"}</td>
                </tr>
              ))}
              {entries.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                    No audit entries yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
