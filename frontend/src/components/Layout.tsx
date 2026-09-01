import { NavLink, Outlet } from "react-router-dom";

const NAV_ITEMS: { to: string; label: string }[] = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/assets", label: "Asset Inventory" },
  { to: "/threat-modeling", label: "Threat Modeling" },
  { to: "/attack-paths", label: "Attack Paths" },
  { to: "/vulnerabilities", label: "Vulnerabilities" },
  { to: "/risk-register", label: "Risk Register" },
  { to: "/iam", label: "IAM Risk" },
  { to: "/cloud", label: "Cloud Security" },
  { to: "/incidents", label: "Incidents" },
  { to: "/controls", label: "Controls" },
  { to: "/evidence", label: "Evidence" },
  { to: "/vendors", label: "Vendors" },
  { to: "/data-security", label: "Data Security" },
  { to: "/business-continuity", label: "Business Continuity" },
  { to: "/ai-inventory", label: "AI Inventory" },
  { to: "/ai-security", label: "AI Security" },
  { to: "/rag-security", label: "RAG Security" },
  { to: "/agent-security", label: "Agent Security" },
  { to: "/reports", label: "Reports" },
  { to: "/audit-log", label: "Audit Log" },
  { to: "/settings", label: "Settings" },
];

export default function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>AEGIS</h1>
        <nav>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
