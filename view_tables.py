import sqlite3
def print_table(conn, table_name, limit=5):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nTable: {table_name}")
    print(f"Total Rows: {count}")
    print("-" * 80)
    print(" | ".join(columns))
    print("-" * 80)
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    for row in cursor.fetchall():
        print(" | ".join(str(value)[:30] + ("..." if len(str(value)) > 30 else "") for value in row))
    if count > limit:
        print(f"... and {count - limit} more rows")
def main():
    db_path = 'instance/parking.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'alembic_version'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Database: {db_path}")
        print("=" * 80)
        for table in tables:
            try:
                print_table(conn, table)
            except Exception as e:
                print(f"Error reading table {table}: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
if __name__ == "__main__":
    main()