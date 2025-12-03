from pathlib import Path
import pandas as pd

def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    
    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the target table
        
    Returns:
        int: Number of rows loaded
    """
    # Check if CSV file exists
    if not Path(csv_path).exists():
        print(f"⚠️ File not found: {csv_path}")
        return 0

    # Read CSV using pandas.read_csv()
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"⚠️ Error reading CSV file: {e}")
        return 0

    # Use df.to_sql() to insert data
    try:
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        print(f"✅ Successfully loaded {len(df)} rows into '{table_name}' table.")
        return len(df)
    except Exception as e:
        print(f"⚠️ Error loading data into table: {e}")
        return 0