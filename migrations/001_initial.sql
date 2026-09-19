CREATE TABLE IF NOT EXISTS artisans (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL CHECK (length(name) BETWEEN 2 AND 80),
    job VARCHAR(60) NOT NULL CHECK (length(job) BETWEEN 2 AND 60),
    neighborhood VARCHAR(80) NOT NULL CHECK (length(neighborhood) BETWEEN 2 AND 80),
    phone VARCHAR(32) NOT NULL CHECK (length(phone) BETWEEN 8 AND 32),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_artisans_job ON artisans(job);
CREATE INDEX IF NOT EXISTS ix_artisans_created_at ON artisans(created_at);
