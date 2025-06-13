import logging

logger = logging.getLogger("data_generator.writers.excel")

def excelWriter(df, params):
    """
    Write DataFrame to an Excel file.
    
    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters for to_excel method, must include 'path_or_buf' or 'excel_writer'
    
    Returns:
        None
    """
    try:
        path = params.get('path_or_buf', params.get('excel_writer'))
        if not path:
            raise ValueError("Missing 'path_or_buf' parameter for Excel writer")
            
        # Default to not including the index
        if 'index' not in params:
            params['index'] = False
            
        logger.info(f"Writing DataFrame with {len(df)} rows to Excel file: {path}")
        df.to_excel(**params)
        logger.info(f"Successfully wrote Excel file: {path}")
        
    except Exception as e:
        logger.error(f"Error writing Excel file: {str(e)}")
        raise
