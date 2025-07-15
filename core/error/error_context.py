from typing import TypedDict, Optional, Any, Dict

class ErrorContext(TypedDict, total=False):
    """Type definition for error context options"""
    generator: Optional[str]
    strategy_name: Optional[str]
    strategy_params: Optional[Dict[str, Any]]
    config: Optional[Dict[str, Any]]
    batch: Optional[Dict[str, Any]]
    stream: Optional[Dict[str, Any]]
    perf_report: Optional[Dict[str, Any]]
    log_level: Optional[str]
    column: Optional[str]
    row: Optional[int]
    value: Optional[Any]
    config_path: Optional[str]


class ErrorContextBuilder:
    def __init__(self):
        self.context = {
            'generator': None,
            'strategy_name': None,
            'strategy_params': None,
            'config': None,
            'batch': None,
            'stream': None,
            'perf_report': None,
            'log_level': None,
            'column': None,
            'row': None,
            'config_path': None,
            'value': None
        }
    
    def with_generator(self, generator: str) -> 'ErrorContextBuilder':
        self.context['generator'] = generator
        return self
        
    def with_strategy_name(self, strategy_name: str) -> 'ErrorContextBuilder':
        self.context['strategy_name'] = strategy_name
        return self
        
    def with_strategy_params(self, strategy_params: dict) -> 'ErrorContextBuilder':
        self.context['strategy_params'] = strategy_params
        return self
        
    def with_config(self, config: dict) -> 'ErrorContextBuilder':
        self.context['config'] = config
        return self
        
    def with_batch(self, batch: dict) -> 'ErrorContextBuilder':
        self.context['batch'] = batch
        return self
        
    def with_stream(self, stream: dict) -> 'ErrorContextBuilder':
        self.context['stream'] = stream
        return self
        
    def with_perf_report(self, perf_report: dict) -> 'ErrorContextBuilder':
        self.context['perf_report'] = perf_report
        return self
        
    def with_log_level(self, log_level: str) -> 'ErrorContextBuilder':
        self.context['log_level'] = log_level
        return self
        
    def with_column(self, column: str) -> 'ErrorContextBuilder':
        self.context['column'] = column
        return self
        
    def with_row(self, row: int) -> 'ErrorContextBuilder':
        self.context['row'] = row
        return self
        
    def with_value(self, value: Any) -> 'ErrorContextBuilder':
        self.context['value'] = value
        return self
        
    def with_config_path(self, config_path: str) -> 'ErrorContextBuilder':
        self.context['config_path'] = config_path
        return self
        
    def build(self) -> ErrorContext:
        return ErrorContext(
            generator=self.context['generator'],
            strategy_name=self.context['strategy_name'],
            strategy_params=self.context['strategy_params'],
            config=self.context['config'],
            batch=self.context['batch'],
            stream=self.context['stream'],
            perf_report=self.context['perf_report'],
            log_level=self.context['log_level'],
            column=self.context['column'],
            row=self.context['row'],
            config_path=self.context['config_path'],
            value=self.context['value']
        )