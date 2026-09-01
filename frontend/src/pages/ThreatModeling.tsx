import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Threat, ThreatActor } from "../api/types";

export default function ThreatModeling() {
  const [actors, setActors] = useState<ThreatActor[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([apiClient.get<ThreatActor[]>("/threat-actors"), apiClient.get<Threat[]>("/threats")])
      .then(([actorsRes, threatsRes]) => {
        setActors(actorsRes.data);
        setThreats(threatsRes.data);
      })
      .catch(() => setError("Could not load the threat model."))
      .finally(() => setLoading(false));
  }, []);

  const actorById = new Map(actors.map((a) => [a.id, a]));

  return (
    <div>
      <h1 className="page-title">Threat Modeling</h1>
      <p className="page-subtitle">
        Threat actors and the specific technique catalog built against Northstar Financial Services'
        actual architecture — every entry explains why it matters here, not just a MITRE ID lookup.
      </p>

      {error && <div className="card" style={{ color: "var(--critical)" }}>{error}</div>}
      {loading && !error && <div className="card">Loading...</div>}

      {!loading && !error && (
        <>
          <h2 style={{ fontSize: 15, marginBottom: 10 }}>Threat Actors</h2>
          <div className="card-grid">
            {actors.map((actor) => (
              <div className="card" key={actor.id}>
                <div style={{ fontWeight: 600 }}>{actor.name}</div>
                <div className="metric-label" style={{ marginTop: 4 }}>{actor.category.replace(/_/g, " ")}</div>
                <div style={{ fontSize: 13, marginTop: 8 }}>{actor.motivation}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>
                  Sophistication: {actor.sophistication}
                </div>
              </div>
            ))}
          </div>

          <h2 style={{ fontSize: 15, margin: "24px 0 10px" }}>Threat Catalog</h2>
          {threats.map((threat) => (
            <div className="card" key={threat.id} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <strong>{threat.name}</strong>
                {threat.mitre_technique_id && (
                  <span className="metric-label">
                    {threat.mitre_technique_id} — {threat.mitre_technique_name}
                  </span>
                )}
              </div>
              <p style={{ fontSize: 13, margin: "8px 0" }}>{threat.description}</p>
              <div style={{ fontSize: 13, background: "var(--bg)", padding: "8px 10px", borderRadius: 6 }}>
                <strong>Why this matters here: </strong>
                {threat.why_relevant}
              </div>
              {threat.threat_actor_id && actorById.get(threat.threat_actor_id) && (
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 8 }}>
                  Associated actor: {actorById.get(threat.threat_actor_id)!.name}
                </div>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
