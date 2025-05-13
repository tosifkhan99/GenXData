import logging

logger = logging.getLogger("data_generator.writers.parquet")

def parquetWriter(df, params):
    """
    Write DataFrame to Parquet format.
    
    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters for to_parquet method, must include 'path'
    
    Returns:
        None
    """
    try:
        path = params.get('path')
        if not path:
            raise ValueError("Missing 'path' parameter for Parquet writer")
        
        # Remove path from params since we'll pass it explicitly
        writer_params = {k: v for k, v in params.items() if k != 'path'}
        
        logger.info(f"Writing DataFrame with {len(df)} rows to Parquet file: {path}")
        df.to_parquet(path, **writer_params)
        logger.info(f"Successfully wrote Parquet file: {path}")
    except ImportError:
        logger.error("pyarrow or fastparquet package is required for Parquet support")
        raise
    except Exception as e:
        logger.error(f"Error writing Parquet file: {str(e)}")
        raise 