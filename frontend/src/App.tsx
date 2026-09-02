import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Assets from "./pages/Assets";
import ThreatModeling from "./pages/ThreatModeling";
import AttackPaths from "./pages/AttackPaths";
import RiskRegister from "./pages/RiskRegister";
import Vulnerabilities from "./pages/Vulnerabilities";
import IAMRisk from "./pages/IAMRisk";
import CloudSecurity from "./pages/CloudSecurity";
import AppSecurity from "./pages/AppSecurity";
import ModulePlaceholder from "./pages/ModulePlaceholder";

function ProtectedRoutes() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Layout />;
}

const PLACEHOLDER_MODULES: { path: string; title: string; phase: string }[] = [
  { path: "incidents", title: "Incident Response", phase: "Phase 7" },
  { path: "controls", title: "Control Assessment", phase: "Phase 8" },
  { path: "evidence", title: "Evidence Management", phase: "Phase 8" },
  { path: "vendors", title: "Third-Party / Vendor Risk", phase: "Phase 9" },
  { path: "data-security", title: "Data Security", phase: "Phase 9" },
  { path: "business-continuity", title: "Business Continuity & DR", phase: "Phase 9" },
  { path: "ai-inventory", title: "AI Inventory", phase: "Phase 10" },
  { path: "ai-security", title: "AI Security", phase: "Phase 10" },
  { path: "rag-security", title: "RAG Security", phase: "Phase 11" },
  { path: "agent-security", title: "AI Agent Security", phase: "Phase 11" },
  { path: "reports", title: "Reports", phase: "Phase 13" },
  { path: "audit-log", title: "Audit Log", phase: "Phase 8" },
  { path: "settings", title: "Settings", phase: "Phase 1" },
];

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoutes />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/assets" element={<Assets />} />
          <Route path="/threat-modeling" element={<ThreatModeling />} />
          <Route path="/attack-paths" element={<AttackPaths />} />
          <Route path="/risk-register" element={<RiskRegister />} />
          <Route path="/vulnerabilities" element={<Vulnerabilities />} />
          <Route path="/iam" element={<IAMRisk />} />
          <Route path="/cloud" element={<CloudSecurity />} />
          <Route path="/app-security" element={<AppSecurity />} />
          {PLACEHOLDER_MODULES.map((m) => (
            <Route
              key={m.path}
              path={`/${m.path}`}
              element={<ModulePlaceholder title={m.title} phase={m.phase} />}
            />
          ))}
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
