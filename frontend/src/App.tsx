import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Assets from "./pages/Assets";
import ModulePlaceholder from "./pages/ModulePlaceholder";

function ProtectedRoutes() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Layout />;
}

const PLACEHOLDER_MODULES: { path: string; title: string; phase: string }[] = [
  { path: "threat-modeling", title: "Threat Modeling", phase: "Phase 2" },
  { path: "attack-paths", title: "Attack Paths", phase: "Phase 2" },
  { path: "vulnerabilities", title: "Vulnerability Management", phase: "Phase 4" },
  { path: "risk-register", title: "Risk Register", phase: "Phase 3" },
  { path: "iam", title: "IAM Risk", phase: "Phase 5" },
  { path: "cloud", title: "Cloud Security Posture", phase: "Phase 5" },
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
