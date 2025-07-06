"""
Streaming processing functionality for GenXData.
"""
import pandas as pd
import configs.GENERATOR_SETTINGS as SETTINGS
from core.processing import process_config
from core.batch_processing import get_batches, prepare_batch_config


def process_streaming_config(config_file, stream_config, debug_mode=False, perf_report=False):
    """
    Process configuration in streaming mode.
    
    Args:
        config_file (dict): Configuration data
        stream_config (dict): Streaming configuration
        debug_mode (bool): Whether to run in debug mode
        perf_report (bool): Whether to generate a performance report
        
    Returns:
        dict: Results with last batch data
    """
    
    # Initialize state tracking for the entire streaming session
    strategy_states = {}
    
    # Get streaming configuration
    streaming_config = stream_config.get('streaming', {})
    
    # Get batch size from streaming config or use default
    batch_size = streaming_config.get('batch_size', SETTINGS.STREAM_BATCH_SIZE)
    batches = get_batches(batch_size, config_file['num_of_rows'])
    
    # Initialize queue producer using the factory
    queue_producer = None
    try:
        from queue.factory import QueueFactory
        queue_producer = QueueFactory.create_from_config(stream_config)
        queue_producer.connect()
        
        
    except ImportError as e:
        raise ValueError(f"Queue library not available: {e}")
    except Exception as e:
        raise ValueError(f"Could not connect to queue: {e}")
    
    df = None
    for batch_index, batch_size in enumerate(batches):
        
        # Pre-calculate and modify config for this batch
        batch_config = prepare_batch_config(config_file, batch_size, batch_index, strategy_states)
        
        df = process_config(batch_config, debug_mode, perf_report)
        
        # Send batch to queue if producer is available
        if queue_producer:
            batch_info = {
                'batch_index': batch_index,
                'batch_size': batch_size,
                'total_batches': len(batches),
                'config_name': config_file.get('metadata', {}).get('name', 'unknown'),
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            # Include additional metadata if configured
            if streaming_config.get('include_metadata', True):
                batch_info['streaming_config'] = streaming_config
            
            queue_producer.send_dataframe(df, batch_info)
    
    # Clean up queue producer
    if queue_producer:
        queue_producer.disconnect()
    
    # Return the last batch as the result
    return {'df': df.to_dict(orient='records') if df is not None else []} 