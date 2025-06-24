import psycopg2
import os

REQUIRED_COLUMNS = [
    ("tech_stack", "JSONB"),
    ("key_features", "TEXT[]"),
    ("tags", "TEXT[]"),
    ("similar_industries", "TEXT[]")
]

def ensure_columns():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    for col, coltype in REQUIRED_COLUMNS:
        cur.execute(f"ALTER TABLE projects ADD COLUMN IF NOT EXISTS {col} {coltype};")
    conn.commit()
    cur.close()
    conn.close()
    print("Ensured all required columns exist in 'projects' table.")

if __name__ == "__main__":
    ensure_columns() 