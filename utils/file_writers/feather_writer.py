import logging

logger = logging.getLogger("data_generator.writers.feather")

def featherWriter(df, params):
    """
    Write DataFrame to a Feather file.
    
    Feather is a fast, lightweight binary columnar format that is designed for high-performance
    data interoperability between multiple languages and environments.
    
    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters including:
            - path (str): Path to output Feather file
            - compression (str, optional): Compression algorithm ('zstd', 'lz4', 'uncompressed')
            - chunksize (int, optional): Number of rows per chunk for writing large files
    
    Returns:
        None
    """
    try:
        path = params.get('path')
        if not path:
            raise ValueError("Missing 'path' parameter for Feather writer")
            
        # Set defaults for common parameters
        compression = params.get('compression', 'zstd')
        
        logger.info(f"Writing DataFrame with {len(df)} rows to Feather file: {path}")
        
        # Create a copy of params without 'path' and any None values
        writer_params = {k: v for k, v in params.items() if k != 'path' and v is not None}
        
        # Write the dataframe to a Feather file
        df.to_feather(path, **writer_params)
        
        logger.info(f"Successfully wrote Feather file: {path}")
        
    except ImportError:
        logger.error("pyarrow package is required for Feather support")
        raise
    except Exception as e:
        logger.error(f"Error writing Feather file: {str(e)}")
        raise 