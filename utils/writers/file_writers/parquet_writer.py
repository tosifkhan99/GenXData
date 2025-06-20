import logging
import os

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
        # Support multiple path parameter names for flexibility
        path = params.get('output_path') or params.get('path')
        if not path:
            raise ValueError("Missing path parameter (use 'output_path' or 'path') for Parquet writer")
        
        # Ensure the file has .parquet extension
        if not path.endswith('.parquet'):
            path = os.path.splitext(path)[0] + '.parquet'
        
        # Remove path-related keys from params since we'll pass path explicitly
        writer_params = {k: v for k, v in params.items() if k not in ['output_path', 'path']}
        
        # Set default compression if not specified
        if 'compression' not in writer_params:
            writer_params['compression'] = 'snappy'
        
        logger.info(f"Writing DataFrame with {len(df)} rows to Parquet file: {path}")
        df.to_parquet(path, **writer_params)
        logger.info(f"Successfully wrote Parquet file: {path}")
    except ImportError:
        logger.error("pyarrow or fastparquet package is required for Parquet support")
        raise
    except Exception as e:
        logger.error(f"Error writing Parquet file: {str(e)}")
        raise 