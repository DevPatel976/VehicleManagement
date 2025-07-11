import sqlite3
def print_table(conn, table_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"\n{'='*50}")
        print(f"TABLE: {table_name}")
        print(f"{'='*50}")
        print(" | ".join(columns))
        print("-" * 100)
        for row in rows:
            print(" | ".join(str(value) for value in row))
        print(f"\nTotal rows: {len(rows)}\n")
    except Exception as e:
        print(f"Error reading table {table_name}: {str(e)}")
def main():
    try:
        db_path = 'instance/parking.db'
        print(f"Attempting to connect to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall() if table[0] != 'alembic_version']
        for table in tables:
            print_table(conn, table)
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
if __name__ == "__main__":
    main()