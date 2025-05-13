import logging

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
        path = params.get('output_path')
        params['path_or_buf'] = path
        if not path:
            raise ValueError("Missing 'path_or_buf' parameter for CSV writer")
            
        # Default to not including the index
        if 'index' not in params:
            params['index'] = False
            
        logger.info(f"Writing DataFrame with {len(df)} rows to CSV file: {path}")
        df.to_csv(path_or_buf=path, index=False)
        logger.info(f"Successfully wrote CSV file: {path}")
        
    except Exception as e:
        logger.error(f"Error writing CSV file: {str(e)}")
        raise