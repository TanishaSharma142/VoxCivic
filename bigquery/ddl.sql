CREATE TABLE IF NOT EXISTS `{{project}}.{{dataset}}.complaints` (
  complaint_id STRING NOT NULL,
  citizen_id STRING,
  category STRING NOT NULL,
  severity INT64 NOT NULL,
  description STRING NOT NULL,
  image_url STRING,
  embedding ARRAY<FLOAT64>,
  ward STRING NOT NULL,
  latitude FLOAT64,
  longitude FLOAT64,
  submitted_at TIMESTAMP NOT NULL,
  status STRING NOT NULL
);

CREATE TABLE IF NOT EXISTS `{{project}}.{{dataset}}.incidents` (
  incident_id STRING NOT NULL,
  complaint_ids ARRAY<STRING> NOT NULL,
  category STRING NOT NULL,
  cluster_size INT64 NOT NULL,
  ward STRING NOT NULL,
  representative_description STRING NOT NULL,
  first_reported_at TIMESTAMP NOT NULL,
  last_reported_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS `{{project}}.{{dataset}}.priority_queue` (
  incident_id STRING NOT NULL,
  priority_score FLOAT64 NOT NULL,
  severity_component FLOAT64 NOT NULL,
  frequency_component FLOAT64 NOT NULL,
  location_risk_component FLOAT64 NOT NULL,
  justification_text STRING NOT NULL,
  recommended_department STRING NOT NULL,
  recommended_action STRING NOT NULL,
  rank INT64 NOT NULL
);

CREATE TABLE IF NOT EXISTS `{{project}}.{{dataset}}.trends` (
  ward STRING NOT NULL,
  category STRING NOT NULL,
  period STRING NOT NULL,
  complaint_count INT64 NOT NULL,
  rolling_avg FLOAT64 NOT NULL,
  anomaly_flag BOOL NOT NULL,
  anomaly_score FLOAT64 NOT NULL
);

CREATE TABLE IF NOT EXISTS `{{project}}.{{dataset}}.anomalies` (
  ward STRING NOT NULL,
  category STRING NOT NULL,
  period STRING NOT NULL,
  complaint_count INT64 NOT NULL,
  rolling_avg FLOAT64 NOT NULL,
  anomaly_flag BOOL NOT NULL,
  anomaly_score FLOAT64 NOT NULL
);
