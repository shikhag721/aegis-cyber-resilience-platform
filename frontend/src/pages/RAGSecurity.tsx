import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { RAGFinding, RAGPipeline } from "../api/types";
import SeverityBadge from "../components/SeverityBadge";

export default function RAGSecurity() {
  const [pipelines, setPipelines] = useState<RAGPipeline[]>([]);
  const [findings, setFindings] = useState<RAGFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiClient.get<RAGPipeline[]>("/rag-security/pipelines"),
      apiClient.get<RAGFinding[]>("/rag-security/gap-analysis"),
    ])
      .then(([pipelinesRes, findingsRes]) => {
        setPipelines(pipelinesRes.data);
        setFindings(findingsRes.data);
      })
      .catch(() => setError("Could not load RAG security data."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="page-title">RAG Security</h1>
      <p className="page-subtitle">
        The same visible symptom — a RAG assistant surfacing information it shouldn't have — can come
        from two different root causes that need different fixes: missing per-document access control
        (broken authorization) or unsanitized retrieved content hijacking the model (prompt injection).
        This gap analysis classifies findings by root cause, not just symptom.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Root-Cause Findings</h2>
          {findings.map((f, i) => (
            <div
              className="card"
              key={i}
              style={{ marginBottom: 8, display: "flex", justifyContent: "space-between" }}
            >
              <div style={{ fontSize: 13 }}>
                <strong>{f.pipeline_name}</strong> —{" "}
                <span style={{ color: "var(--text-muted)" }}>{f.root_cause.replace(/_/g, " ")}</span>
                <br />
                {f.detail}
              </div>
              <SeverityBadge band={f.severity} />
            </div>
          ))}
          {findings.length === 0 && <div className="card">No RAG security findings.</div>}

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>RAG Pipeline Catalog</h2>
          <div className="card" style={{ padding: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Data Sources</th>
                  <th>Doc-Level ACL</th>
                  <th>Content Sanitized</th>
                  <th>Untrusted Sources</th>
                  <th>Sources Validated</th>
                  <th>Output Validated</th>
                </tr>
              </thead>
              <tbody>
                {pipelines.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.data_sources.join(", ")}</td>
                    <td>{p.document_level_access_control ? "Yes" : "No"}</td>
                    <td>{p.retrieved_content_sanitized ? "Yes" : "No"}</td>
                    <td>{p.allows_untrusted_data_sources ? "Yes" : "No"}</td>
                    <td>{p.source_content_validated ? "Yes" : "No"}</td>
                    <td>{p.output_validated_before_use ? "Yes" : "No"}</td>
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
