CREATE SCHEMA raw;
CREATE SCHEMA stage;
CREATE SCHEMA gold;
CREATE SCHEMA meta;

CREATE TABLE meta.build_info (
    manifest_version VARCHAR NOT NULL,
    dataset_slug VARCHAR NOT NULL,
    dataset_version INTEGER NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE meta.raw_manifest (
    file_name VARCHAR NOT NULL,
    expected_bytes BIGINT NOT NULL,
    observed_bytes BIGINT NOT NULL,
    expected_rows BIGINT NOT NULL,
    observed_rows BIGINT NOT NULL,
    expected_sha256 VARCHAR NOT NULL,
    observed_sha256 VARCHAR NOT NULL,
    verified BOOLEAN NOT NULL
);

