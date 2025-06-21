import logging
import os

logger = logging.getLogger("data_generator.writers.csv")

def csvWriter(df, params):
    """
    Write DataFrame to a CSV file.
    
    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters for to_csv method, must include 'path_or_buf'
    
    Returns:
        None
    """
    try:
        # Support multiple path parameter names for flexibility
        path = params.get('output_path') or params.get('path_or_buf')
        if not path:
            raise ValueError("Missing path parameter (use 'output_path' or 'path_or_buf') for CSV writer")
            
        # Ensure the file has .csv extension
        if not path.endswith('.csv'):
            path = os.path.splitext(path)[0] + '.csv'
            
        # Create a copy of params for to_csv call, removing path-related keys
        csv_params = {k: v for k, v in params.items() if k not in ['output_path', 'path_or_buf']}
        
        # Default to not including the index
        if 'index' not in csv_params:
            csv_params['index'] = False
            
        logger.info(f"Writing DataFrame with {len(df)} rows to CSV file: {path}")
        df.to_csv(path, **csv_params)
        logger.info(f"Successfully wrote CSV file: {path}")
        
    except Exception as e:
        logger.error(f"Error writing CSV file: {str(e)}")
        raise