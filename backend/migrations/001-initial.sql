-- Initial demo schema comes from versioned SQLAlchemy metadata.
-- Natural unique keys: consumption_datasets.name, period_comparisons.name, published_reports.run_id.
-- Existing production deployments need reviewed ALTER migrations.
CREATE INDEX IF NOT EXISTS ix_decomposition_runs_status ON decomposition_runs(status);
