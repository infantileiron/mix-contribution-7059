-- 观测修订与版本锁定（在 001-initial.sql 之上）
-- 新部署由 SQLAlchemy metadata 直接建表；已有部署按下列语句手工升级。
CREATE TABLE IF NOT EXISTS observation_revisions (
    id VARCHAR PRIMARY KEY,
    dataset_id VARCHAR NOT NULL REFERENCES consumption_datasets(id),
    reason TEXT NOT NULL,
    author VARCHAR NOT NULL,
    base_version INTEGER NOT NULL,
    new_version INTEGER NOT NULL,
    changes JSON NOT NULL DEFAULT '[]',
    checksum_before VARCHAR NOT NULL,
    checksum_after VARCHAR NOT NULL,
    created_at VARCHAR NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_observation_revisions_dataset
    ON observation_revisions(dataset_id);

ALTER TABLE consumption_datasets
    ADD COLUMN IF NOT EXISTS current_version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE decomposition_runs
    ADD COLUMN IF NOT EXISTS dataset_version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE decomposition_runs
    ADD COLUMN IF NOT EXISTS dataset_snapshot JSON NOT NULL DEFAULT '[]';
ALTER TABLE driver_reviews
    ADD COLUMN IF NOT EXISTS dataset_version INTEGER NOT NULL DEFAULT 1;

-- 说明：升级前已 completed 的运行结果不受影响（结果与校验码已持久化）。
-- 升级瞬间仍处于 queued/running 的遗留运行没有快照，升级后需要时按最新观测重新排队运行。
-- 新排队的运行都会写入 dataset_version 与 dataset_snapshot，worker 仅按快照计算。
