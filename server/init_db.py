# init_db.py
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()

# Read DB connection params from environment (recommended)
DB_CONFIG = {
    "host":     os.getenv("PGHOST", "localhost"),
    "port":     int(os.getenv("PGPORT", "5432")),
    "dbname":   os.getenv("PGDATABASE", "hiro_db"),
    "user":     os.getenv("PGUSER", "hiro_user"),
    "password": os.getenv("PGPASSWORD", "ChangeThisStrongPW!"),
}

CREATE_TABLE_SQL = """
-- optional: enable pgcrypto so we can later use gen_random_uuid() if needed
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS applicants (
    id UUID PRIMARY KEY,                                   -- applicant_id (unique)
    name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('pending','shortlisted','rejected','hired')),
    email VARCHAR(320) UNIQUE NOT NULL,
    telephone VARCHAR(50),
    job_applied VARCHAR(200) NOT NULL,                     -- applied position
    applied_date DATE NOT NULL DEFAULT CURRENT_DATE,
    score NUMERIC(5,2),                                    -- can be NULL (N/A)
    resume VARCHAR(255),                                   -- file path / URL
    prior_experience TEXT,                                 -- free text / companies
    source VARCHAR(120),                                   -- optional
    skills TEXT[] NOT NULL DEFAULT '{}'::text[]            -- array of skills
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_applicants_status ON applicants(status);
CREATE INDEX IF NOT EXISTS idx_applicants_applied_date ON applicants(applied_date);
"""

CHECK_TABLE_SQL = """
SELECT EXISTS (
  SELECT 1
  FROM information_schema.tables
  WHERE table_schema = 'public' AND table_name = 'applicants'
) AS table_exists;
"""

def connect():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print("❌ Failed to connect to PostgreSQL:", e)
        sys.exit(1)

def ensure_table(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(CHECK_TABLE_SQL)
        exists = cur.fetchone()["table_exists"]
        if exists:
            print("✅ Table 'applicants' already exists; no action taken.")
            return False
        else:
            cur.execute(CREATE_TABLE_SQL)
            print("✅ Table 'applicants' created successfully.")
            return True

def main():
    print(f"Connecting to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']} db='{DB_CONFIG['dbname']}' as user '{DB_CONFIG['user']}'")
    conn = connect()
    try:
        created = ensure_table(conn)
        if created:
            print("Done.")
        else:
            print("Nothing to do.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
