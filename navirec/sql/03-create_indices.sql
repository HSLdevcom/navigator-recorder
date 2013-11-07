CREATE INDEX TraceTimestampIndex ON Traces (timestamp_utc);
CREATE INDEX UserAgentIndex ON Sessions (user_agent);
