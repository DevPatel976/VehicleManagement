import sqlite3
def print_database_info():
    try:
        conn = sqlite3.connect('instance/parking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("="*70)
        print("DATABASE TABLES")
        print("="*70)
        for table in tables:
            table_name = table[0]
            if table_name == 'alembic_version':
                continue
            print("\n" + "-"*70)
            print(f"TABLE: {table_name}")
            print("-"*70)
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("COLUMNS:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"\nTOTAL ROWS: {row_count}")
            if row_count > 0:
                print("\nFIRST 5 ROWS:")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                col_names = [col[1] for col in columns]
                print("  " + " | ".join(col_names))
                print("  " + "-" * (sum(len(name) for name in col_names) + 3 * (len(col_names) - 1)))
                for row in rows:
                    print("  " + " | ".join(str(value) for value in row))
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
if __name__ == "__main__":
    print_database_info()