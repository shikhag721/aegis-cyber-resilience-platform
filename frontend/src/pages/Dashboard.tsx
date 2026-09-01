import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

export default function Dashboard() {
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "error">("checking");

  useEffect(() => {
    apiClient
      .get("/health")
      .then(() => setApiStatus("ok"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <div>
      <h1 className="page-title">Executive Dashboard</h1>
      <p className="page-subtitle">
        Northstar Financial Services - security posture overview. Full metrics land in Phase 13; this
        phase confirms the frontend/backend/database foundation is wired end to end.
      </p>
      <div className="card-grid">
        <div className="card">
          <div className="metric-label">Backend API</div>
          <div className="metric-value">
            {apiStatus === "checking" && "Checking..."}
            {apiStatus === "ok" && "Connected"}
            {apiStatus === "error" && "Unreachable"}
          </div>
        </div>
      </div>
      <div className="card">
        Dashboard metrics (critical risks, overdue remediation, control gaps, AI risk, etc.) will appear
        here once the risk engine, asset inventory, and control-assessment modules are built - see
        CHANGELOG.md for phase status.
      </div>
    </div>
  );
}
