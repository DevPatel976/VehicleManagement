import sqlite3
import pandas as pd
from datetime import datetime
def get_db_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall() if table[0] != 'alembic_version']
def get_table_data(conn, table_name):
    try:
        query = f"SELECT * FROM {table_name} LIMIT 100"
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error reading table {table_name}: {str(e)}")
        return pd.DataFrame()
def generate_html(tables_data):
    html = .format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for table_name, df in tables_data.items():
        if not df.empty:
            html += f
    html +=
    return html
def main():
    try:
        conn = sqlite3.connect('instance/parking.db')
        tables = get_db_tables(conn)
        tables_data = {}
        for table in tables:
            df = get_table_data(conn, table)
            if not df.empty:
                tables_data[table] = df
        html_content = generate_html(tables_data)
        output_file = 'database_viewer.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Database viewer generated successfully: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
if __name__ == "__main__":
    main()