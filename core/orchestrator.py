"""
Main orchestrator for GenXData processing.
"""
import configs.GENERATOR_SETTINGS as SETTINGS
from utils.config_utils import load_config, get_config_files
from core.processing import process_config
from core.streaming import process_streaming_config, process_batch_config


class DataOrchestrator:
    """
    Orchestrator class for data generation processing.
    """
    def __init__(self, config, perf_report=SETTINGS.PERF_REPORT, stream=None, batch=None):
        """
        Initialize the DataOrchestrator.
        
        Args:
            config (dict): Configuration dictionary
            perf_report (bool): Whether to generate performance report
            stream (str): Path to streaming config file
            batch (str): Path to batch config file
        """
        self.config = config
        self.perf_report = perf_report
        self.stream = stream
        self.batch = batch


    
    def run(self):
        """
        Run the data generation process.
        
        Returns:
            dict: Processing results
        """
        try:
            if self.stream and self.batch:
                raise ValueError("Streaming and batch modes are not supported together")
        
            if isinstance(self.config, str):
                config_files = get_config_files(self.config)
            else:
                config_files = [self.config]
    
            if self.stream:
                stream_config = load_config(self.stream)
                return process_streaming_config(self.config, stream_config, False, self.perf_report)
            elif self.batch:
                batch_config = load_config(self.batch)
                return process_batch_config(self.config, batch_config, False, self.perf_report)
            else:
                df = process_config(self.config, False, self.perf_report)
                return {'df': df.to_dict(orient='records')}
                
        except Exception as e:
            raise
