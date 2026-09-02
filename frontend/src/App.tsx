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
import Incidents from "./pages/Incidents";
import Controls from "./pages/Controls";
import Evidence from "./pages/Evidence";
import AuditLog from "./pages/AuditLog";
import Vendors from "./pages/Vendors";
import DataSecurity from "./pages/DataSecurity";
import BusinessContinuity from "./pages/BusinessContinuity";
import AIInventory from "./pages/AIInventory";
import AISecurity from "./pages/AISecurity";
import ModulePlaceholder from "./pages/ModulePlaceholder";

function ProtectedRoutes() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Layout />;
}

const PLACEHOLDER_MODULES: { path: string; title: string; phase: string }[] = [
  { path: "rag-security", title: "RAG Security", phase: "Phase 11" },
  { path: "agent-security", title: "AI Agent Security", phase: "Phase 11" },
  { path: "reports", title: "Reports", phase: "Phase 13" },
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
          <Route path="/incidents" element={<Incidents />} />
          <Route path="/controls" element={<Controls />} />
          <Route path="/evidence" element={<Evidence />} />
          <Route path="/audit-log" element={<AuditLog />} />
          <Route path="/vendors" element={<Vendors />} />
          <Route path="/data-security" element={<DataSecurity />} />
          <Route path="/business-continuity" element={<BusinessContinuity />} />
          <Route path="/ai-inventory" element={<AIInventory />} />
          <Route path="/ai-security" element={<AISecurity />} />
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
