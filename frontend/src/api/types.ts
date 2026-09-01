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
