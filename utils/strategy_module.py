import importlib.util
def load_strategy_module(module_path):
    spec = importlib.util.spec_from_file_location(name="strategy_module" ,location= module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module