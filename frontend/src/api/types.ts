export type AssetType =
  | "server"
  | "endpoint"
  | "api"
  | "application"
  | "database"
  | "cloud_resource"
  | "container"
  | "identity"
  | "saas"
  | "network_device"
  | "ai_system";

export type Environment = "production" | "staging" | "development" | "test";

export type Criticality = "low" | "medium" | "high" | "critical";

export type DataClassification =
  | "public"
  | "internal"
  | "confidential"
  | "restricted"
  | "highly_restricted";

export interface ThreatActor {
  id: number;
  name: string;
  category: string;
  motivation: string;
  sophistication: string;
  description: string;
}

export interface Threat {
  id: number;
  name: string;
  description: string;
  threat_actor_id: number | null;
  mitre_technique_id: string | null;
  mitre_technique_name: string | null;
  why_relevant: string;
}

export interface AttackPathStep {
  id: number;
  sequence: number;
  description: string;
  asset_id: number | null;
  threat_id: number | null;
}

export interface AttackPath {
  id: number;
  name: string;
  description: string;
  entry_point: string;
  target_asset_id: number;
  likelihood: number;
  impact: number;
  score: number;
  notes: string;
  steps: AttackPathStep[];
}

export interface RiskFactorEntry {
  name: string;
  axis: "likelihood" | "impact";
  weight: number;
  reason: string;
}

export interface RiskRecord {
  id: number;
  title: string;
  description: string;
  asset_id: number;
  threat_id: number | null;
  attack_path_id: number | null;
  asset_criticality: string;
  data_classification: string;
  threat_severity: string;
  internet_exposed: boolean;
  known_exploited: boolean;
  logging_enabled: boolean;
  control_effectiveness: number;
  risk_appetite: string;
  likelihood: number;
  impact: number;
  inherent_score: number;
  inherent_rating: string;
  residual_score: number;
  residual_rating: string;
  contributing_factors: RiskFactorEntry[];
  primary_concern: string;
  recommended_treatment: string;
  treatment_decision: string | null;
  treatment_reason: string;
  owner: string;
  target_date: string | null;
  status: string;
}

export interface Vulnerability {
  id: number;
  cve_id: string | null;
  title: string;
  description: string;
  asset_id: number;
  cvss_score: number;
  cvss_severity_band: string;
  known_exploited: boolean;
  compensating_controls: string;
  remediation_status: string;
  owner: string;
  due_date: string | null;
  risk_record_id: number | null;
}

export interface IdentityAccount {
  id: number;
  username: string;
  display_name: string;
  account_type: string;
  department: string;
  employment_status: string;
  is_enabled: boolean;
  is_privileged: boolean;
  mfa_enabled: boolean;
  production_access: boolean;
  permissions: string[];
  last_login_at: string | null;
}

export interface IAMFinding {
  account_username: string;
  finding_type: string;
  severity: string;
  detail: string;
}

export interface CloudFinding {
  id: number;
  resource_name: string;
  asset_id: number | null;
  finding_type: string;
  severity: string;
  description: string;
  recommendation: string;
  status: string;
}

export interface AppSecFinding {
  id: number;
  resource_name: string;
  asset_id: number | null;
  finding_type: string;
  severity: string;
  description: string;
  owasp_reference: string;
  recommendation: string;
  status: string;
}

export interface SecretFinding {
  id: number;
  secret_type: string;
  location: string;
  severity: string;
  exposure: string;
  redacted_snippet: string;
  rotation_recommendation: string;
  status: string;
}

export interface CorrelationFinding {
  username: string;
  severity: string;
  matched_event_types: string[];
  narrative: string;
}

export interface IncidentTimelineEntry {
  id: number;
  stage: string;
  description: string;
  occurred_at: string;
}

export interface Incident {
  id: number;
  title: string;
  description: string;
  severity: string;
  stage: string;
  affected_asset_ids: number[];
  indicators: string[];
  recommended_containment: string;
  remediation: string;
  lessons_learned: string;
  detected_at: string;
  timeline: IncidentTimelineEntry[];
}

export interface Asset {
  id: number;
  asset_tag: string;
  name: string;
  asset_type: AssetType;
  owner: string;
  business_unit: string;
  environment: Environment;
  criticality: Criticality;
  data_classification: DataClassification;
  internet_exposed: boolean;
  technology: string;
  authentication_method: string;
  encrypted: boolean;
  logging_enabled: boolean;
  backup_enabled: boolean;
  notes: string;
}
