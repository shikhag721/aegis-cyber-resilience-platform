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
