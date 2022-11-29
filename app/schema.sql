DROP TABLE IF EXISTS metrics;
CREATE TABLE metrics (
    Id integer primary key autoincrement,
    hostname text,
    port text,
    remoteAddr text,
    timestamp real
)
