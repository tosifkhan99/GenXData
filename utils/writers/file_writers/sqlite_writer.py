import logging
import sqlite3
import os

logger = logging.getLogger("data_generator.writers.sqlite")

def sqliteWriter(df, params):
    """
    Write DataFrame to a SQLite database.
    
    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters including:
            - database (str): Path to SQLite database file
            - table (str): Name of the table to write to
            - if_exists (str): How to behave if the table exists ('fail', 'replace', 'append')
            - index (bool): Write DataFrame index as a column
    
    Returns:
        None
    """
    try:
        # Support multiple path parameter names for flexibility
        database = params.get('output_path') or params.get('database')
        table = params.get('table', 'data')  # Default table name
        if_exists = params.get('if_exists', 'replace')
        index = params.get('index', False)
        
        if not database:
            raise ValueError("Missing database path parameter (use 'output_path' or 'database') for SQLite writer")
            
        # Ensure the file has .db extension
        if not database.endswith(('.db', '.sqlite', '.sqlite3')):
            database = os.path.splitext(database)[0] + '.db'
            
        logger.info(f"Writing DataFrame with {len(df)} rows to SQLite database: {database}, table: {table}")
        
        # Create a SQLite connection
        conn = sqlite3.connect(database)
        
        # Write the DataFrame to SQLite
        df.to_sql(
            name=table,
            con=conn,
            if_exists=if_exists,
            index=index
        )
        
        # Close the connection
        conn.close()
        
        logger.info(f"Successfully wrote to SQLite table: {table}")
        
    except Exception as e:
        logger.error(f"Error writing to SQLite: {str(e)}")
        raise 