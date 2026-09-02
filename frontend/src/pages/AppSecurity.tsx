import { FormEvent, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { AppSecFinding, SecretFinding } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

export default function AppSecurity() {
  const [findings, setFindings] = useState<AppSecFinding[]>([]);
  const [secrets, setSecrets] = useState<SecretFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [scanText, setScanText] = useState("");
  const [scanLocation, setScanLocation] = useState("");
  const [scanResult, setScanResult] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    Promise.all([
      apiClient.get<AppSecFinding[]>("/app-security/findings"),
      apiClient.get<SecretFinding[]>("/app-security/secrets"),
    ])
      .then(([findingsRes, secretsRes]) => {
        setFindings(findingsRes.data);
        setSecrets(secretsRes.data);
      })
      .catch(() => setError("Could not load application security data."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  async function handleScan(e: FormEvent) {
    e.preventDefault();
    setScanResult(null);
    try {
      const res = await apiClient.post<SecretFinding[]>("/app-security/secrets/scan", {
        text: scanText,
        location: scanLocation || "Pasted snippet",
      });
      setScanResult(
        res.data.length > 0
          ? `Found and recorded ${res.data.length} potential secret(s).`
          : "No secrets detected in this text."
      );
      setScanText("");
      load();
    } catch {
      setScanResult("Scan failed — check your permissions.");
    }
  }

  return (
    <div>
      <h1 className="page-title">Application Security &amp; Secrets</h1>
      <p className="page-subtitle">
        OWASP-referenced application/API findings, plus a real regex-based secret scanner — paste text
        below to check it before committing. Detection only: no real secret is ever stored, only a
        redacted snippet.
      </p>

      <form className="card" style={{ marginBottom: 20 }} onSubmit={handleScan}>
        <div className="field">
          <label>Location (e.g. file path or source)</label>
          <input value={scanLocation} onChange={(e) => setScanLocation(e.target.value)} />
        </div>
        <div className="field">
          <label>Text to scan</label>
          <textarea
            value={scanText}
            onChange={(e) => setScanText(e.target.value)}
            rows={5}
            style={{ width: "100%", padding: 8, border: "1px solid var(--border)", borderRadius: 6, fontFamily: "monospace", fontSize: 12 }}
            placeholder="Paste a config snippet or code to scan for secrets..."
            required
          />
        </div>
        <button className="btn-primary" style={{ width: "auto", padding: "8px 16px" }} type="submit">
          Scan for Secrets
        </button>
        {scanResult && <div style={{ marginTop: 10, fontSize: 13 }}>{scanResult}</div>}
      </form>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Application/API Findings</h2>
          {findings.map((f) => (
            <div className="card" key={f.id} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{f.resource_name}</strong>
                <SeverityBadge band={f.severity} />
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)", margin: "4px 0" }}>
                {f.finding_type.replace(/_/g, " ")} — {f.owasp_reference}
              </div>
              <p style={{ fontSize: 13 }}>{f.description}</p>
              <div style={{ fontSize: 13, background: "var(--bg)", padding: "6px 10px", borderRadius: 6 }}>
                <strong>Recommendation: </strong>
                {f.recommendation}
              </div>
            </div>
          ))}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Secret Findings</h2>
          <div className="card" style={{ padding: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Location</th>
                  <th>Redacted Match</th>
                  <th>Exposure</th>
                  <th>Severity</th>
                </tr>
              </thead>
              <tbody>
                {secrets.map((s) => (
                  <tr key={s.id}>
                    <td>{s.secret_type.replace(/_/g, " ")}</td>
                    <td>{s.location}</td>
                    <td style={{ fontFamily: "monospace", fontSize: 12 }}>{s.redacted_snippet}</td>
                    <td>{s.exposure}</td>
                    <td>
                      <SeverityBadge band={s.severity} />
                    </td>
                  </tr>
                ))}
                {secrets.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ textAlign: "center", color: "var(--text-muted)" }}>
                      No secrets recorded.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
