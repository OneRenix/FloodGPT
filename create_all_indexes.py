import sqlite3

DATABASE_PATH = 'C:\\DEV\\FLOODGPT\\db\\analytics.db'

def create_index_if_not_exists(conn, table_name, columns, index_name):
    cursor = conn.cursor()

    print(f"Processing table: {table_name}")

    # Check if table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    if not cursor.fetchone():
        print(f"  Table '{table_name}' does not exist. Skipping index creation.")
        return

    # Check if all columns exist in the table
    cursor.execute(f"PRAGMA table_info({table_name});")
    table_columns = [col[1] for col in cursor.fetchall()]
    
    missing_columns = [col for col in columns if col not in table_columns]
    if missing_columns:
        print(f"  Missing columns in table '{table_name}': {', '.join(missing_columns)}. Skipping index creation.")
        return

    print(f"  All specified columns {', '.join(columns)} found in {table_name}.")

    # Check if the index already exists by name
    cursor.execute(f"PRAGMA index_list({table_name});")
    indexes = cursor.fetchall()
    index_already_exists = False
    for idx in indexes:
        if idx[1] == index_name: # idx[1] is the index name
            index_already_exists = True
            print(f"  Index '{index_name}' already exists on '{table_name}'.")
            break

    if not index_already_exists:
        columns_str = ', '.join(columns)
        print(f"  Creating index '{index_name}' on ({columns_str}) in {table_name}...")
        cursor.execute(f"CREATE INDEX {index_name} ON {table_name} ({columns_str});")
        print(f"  Index '{index_name}' created successfully.")
    else:
        print(f"  Skipping index creation for {table_name} as it already exists.")

def main():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        
        print("Starting index creation process...")

        # 1. Index for 'constructor_name' in 'cpes_projects'
        create_index_if_not_exists(conn, 'cpes_projects', ['constructor_name'], 'idx_cpes_projects_constructor_name')

        # 2. Composite index for 'flood_control_projects'
        flood_control_cols = ['infra_year', 'region', 'province', 'implementing_office', 'municipality', 'contractor']
        create_index_if_not_exists(conn, 'flood_control_projects', flood_control_cols, 'idx_flood_control_projects_composite')

        # 3. Composite index for 'contractor_name_mapping'
        contractor_mapping_cols = ['canonical_name', 'cpes_name']
        create_index_if_not_exists(conn, 'contractor_name_mapping', contractor_mapping_cols, 'idx_contractor_name_mapping_composite')

        conn.commit()
        print("All specified index creation processes completed.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
