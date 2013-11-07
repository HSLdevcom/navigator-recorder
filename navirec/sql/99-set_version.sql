BEGIN TRANSACTION;

INSERT INTO SchemaVersion
            (schema_id, major_release, minor_release, point_release,
             release_comment, apply_date_utc)
VALUES (1, '01', '00', '0000', 'initial install',
        strftime('%Y-%m-%dT%H:%M:%f', 'now'));

END TRANSACTION;
