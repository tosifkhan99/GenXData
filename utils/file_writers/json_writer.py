import logging
import os

logger = logging.getLogger("data_generator.writers.json")

def jsonWriter(df, params):
    """
    Write DataFrame to a JSON file.
    
    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters for to_json method, must include 'output_path' or 'path_or_buf'
    
    Returns:
        None
    """
    try:
        path = params.get('output_path') or params.get('path_or_buf')
        if not path:
            raise ValueError("Missing 'output_path' or 'path_or_buf' parameter for JSON writer")
            
        # Ensure the file has .json extension
        if not path.endswith('.json'):
            path = os.path.splitext(path)[0] + '.json'
            
        # Set defaults if not provided
        if 'orient' not in params:
            params['orient'] = 'records'
            
        if 'date_format' not in params:
            params['date_format'] = 'iso'
            
        logger.info(f"Writing DataFrame with {len(df)} rows to JSON file: {path}")

        # Create a copy of params for to_json call, using path_or_buf as required by pandas
        json_params = {k: v for k, v in params.items() if k not in ['output_path']}
        json_params['path_or_buf'] = path
        
        df.to_json(**json_params)
        logger.info(f"Successfully wrote JSON file: {path}")
        
    except Exception as e:
        logger.error(f"Error writing JSON file: {str(e)}")
        raise
