CREATE TABLE IF NOT EXISTS certificate_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                port INTEGER NOT NULL,
                check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_valid BOOLEAN,
                days_remaining INTEGER,
                error_message TEXT
            )