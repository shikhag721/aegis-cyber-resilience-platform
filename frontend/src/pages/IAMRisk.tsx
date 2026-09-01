import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { IAMFinding, IdentityAccount } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

export default function IAMRisk() {
  const [findings, setFindings] = useState<IAMFinding[]>([]);
  const [accounts, setAccounts] = useState<IdentityAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiClient.get<IAMFinding[]>("/iam/findings"),
      apiClient.get<IdentityAccount[]>("/iam/accounts"),
    ])
      .then(([findingsRes, accountsRes]) => {
        setFindings(findingsRes.data);
        setAccounts(accountsRes.data);
      })
      .catch(() => setError("Could not load IAM data."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="page-title">IAM Risk</h1>
      <p className="page-subtitle">
        Identity and access findings, detected automatically from account attributes — orphaned
        accounts, missing MFA on privileged access, inactive accounts, inappropriate production access,
        segregation-of-duties conflicts, and privilege-escalation paths.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Findings ({findings.length})</h2>
          {findings.map((f, i) => (
            <div className="card" key={i} style={{ marginBottom: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{f.finding_type.replace(/_/g, " ")}</div>
                <div style={{ fontSize: 13, marginTop: 4 }}>{f.detail}</div>
              </div>
              <SeverityBadge band={f.severity} />
            </div>
          ))}
          {findings.length === 0 && <div className="card">No IAM findings — accounts look clean.</div>}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>All Accounts ({accounts.length})</h2>
          <div className="card" style={{ padding: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Type</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th>Privileged</th>
                  <th>MFA</th>
                  <th>Prod Access</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map((a) => (
                  <tr key={a.id}>
                    <td>{a.username}</td>
                    <td>{a.account_type}</td>
                    <td>{a.department}</td>
                    <td>{a.employment_status}{!a.is_enabled ? " (disabled)" : ""}</td>
                    <td>{a.is_privileged ? "Yes" : "No"}</td>
                    <td>{a.mfa_enabled ? "Yes" : "No"}</td>
                    <td>{a.production_access ? "Yes" : "No"}</td>
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
