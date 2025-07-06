"""
Batch file processing functionality for GenXData.
"""
import pandas as pd
import configs.GENERATOR_SETTINGS as SETTINGS
from core.processing import process_config
from core.batch_processing import get_batches, prepare_batch_config


def process_batch_config(config_file, batch_config, debug_mode=False, perf_report=False):
    """
    Process configuration in batch file mode.
    
    Args:
        config_file (dict): Configuration data
        batch_config (dict): Batch configuration
        debug_mode (bool): Whether to run in debug mode
        perf_report (bool): Whether to generate a performance report
        
    Returns:
        dict: Results with last batch data
    """
    
    # Validate batch configuration
    if 'batch_writer' not in batch_config:
        raise ValueError("Batch config must contain 'batch_writer' section with writer settings")
    
    writer_config = batch_config['batch_writer']
    
    # Required batch writer settings
    if 'output_dir' not in writer_config:
        raise ValueError("Batch writer config must contain 'output_dir' setting")
    
    # Initialize state tracking for the entire batch session
    strategy_states = {}
    
    # Get batch size from batch config or use default
    batch_size = writer_config.get('batch_size', SETTINGS.STREAM_BATCH_SIZE)
    batches = get_batches(batch_size, config_file['num_of_rows'])
    
    # Initialize batch writer
    from writers.batch_writer import BatchWriter
    batch_writer = BatchWriter(
        output_dir=writer_config['output_dir'],
        file_prefix=writer_config.get('file_prefix', 'batch'),
        file_format=writer_config.get('file_format', 'json')
    
    df = None
    for batch_index, batch_size in enumerate(batches):
        
        # Pre-calculate and modify config for this batch
        batch_config_item = prepare_batch_config(config_file, batch_size, batch_index, strategy_states)
        
        df = process_config(batch_config_item, debug_mode, perf_report)
        
        # Write batch to file
        batch_info = {
            'batch_index': batch_index,
            'batch_size': batch_size,
            'total_batches': len(batches),
            'config_name': config_file.get('metadata', {}).get('name', 'unknown'),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        batch_writer.write_batch(df, batch_info)
    
    # Get summary
    summary = batch_writer.get_summary()
    
    # Return the last batch as the result
    return {'df': df.to_dict(orient='records') if df is not None else []} 