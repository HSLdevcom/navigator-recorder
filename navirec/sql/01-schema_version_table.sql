CREATE TABLE SchemaVersion (
    schema_id INT PRIMARY KEY,
    major_release VARCHAR(2) NOT NULL,
    minor_release VARCHAR(2) NOT NULL,
    point_release VARCHAR(4) NOT NULL,
    release_comment VARCHAR(512) NOT NULL,
    -- "YYYY-MM-DDTHH:MM:SS.sss"
    apply_date_utc VARCHAR(23) NOT NULL
);
