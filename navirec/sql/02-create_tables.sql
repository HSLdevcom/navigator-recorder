CREATE TABLE Sessions (
    -- UUID
    session_id VARCHAR(36) PRIMARY KEY,
    user_agent VARCHAR(512) NULL,
    -- "YYYY-MM-DDTHH:MM:SS.sss"
    logged_in_utc VARCHAR(23) NOT NULL
    ---- "YYYY-MM-DDTHH:MM:SS.sss"
    --logged_out_utc VARCHAR(23) NULL
);

CREATE TABLE Traces (
    -- UUID
    trace_id VARCHAR(36) PRIMARY KEY,
    -- UUID
    session_id VARCHAR(36) REFERENCES Sessions (session_id),
    -- "YYYY-MM-DDTHH:MM:SS.sss"
    timestamp_utc VARCHAR(23) NOT NULL,
    accuracy REAL NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    ne_lat DOUBLE PRECISION NULL,
    ne_lng DOUBLE PRECISION NULL,
    sw_lat DOUBLE PRECISION NULL,
    sw_lng DOUBLE PRECISION NULL,
    ---- Just store JSON as VARCHAR.
    --routes VARCHAR(4096) NULL,
    UNIQUE(session_id, timestamp_utc) ON CONFLICT IGNORE
);
