import sqlite3
import pandas as pd
from tabulate import tabulate
def view_database():
    try:
        conn = sqlite3.connect('instance/parking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\n" + "="*50)
        print("DATABASE TABLES")
        print("="*50)
        for table in tables:
            table_name = table[0]
            if table_name == 'alembic_version':
                continue
            print(f"\n{'='*30}")
            print(f"TABLE: {table_name}")
            print(f"{'='*30}")
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [column[1] for column in cursor.fetchall()]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                if not df.empty:
                    print(tabulate(df, headers=columns, tablefmt='grid', showindex=False))
                    print(f"\nTotal rows: {len(df)}")
                else:
                    print("No data found in this table.")
            except Exception as e:
                print(f"Error reading table {table_name}: {str(e)}")
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
if __name__ == "__main__":
    view_database()