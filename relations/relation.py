import logging
from utils.strategy_module import load_strategy_module
from utils.args_to_dict import args_to_dict

logger = logging.getLogger("data_generator.relation")

def compare_type(val):
    """Convert value to appropriate type for comparison"""
    if isinstance(val, str):
        return str(val)
    elif isinstance(val, (int, float)):
        return val
    else:
        # For other types, convert to string for safe comparison
        return str(val)

def relation_type(relation, df, col_name, rows, STRATEGIES, LOGICAL_MAPPING):
    """ 
    Summary:
        creates a set of boolean values also referred as `mask` in the code, to generate some other column based on this mask    
        
    Args:
        relation: holds filter dict which have left hand side operartor referred as `col`, and rhs the value which is going to be compared.
        df: an empty dataframe or a dataframe which is generated from previous strategy or relation.
        col_name: column for which the data to be generate.
        rows: number of rows to generate.
        STRATEGIES: type of strategy which is used to generate col_name.
        LOGICAL_MAPPING: a constant wrapper for strategy file config.

    Returns:
        df : an updated dataframe.
    """
    mask = None

    try:
        # Standardize operation name
        operation = relation.get('operation', 'overwrite')
        if operation == 'insert':
            operation = 'overwrite'
        elif operation == 'insertIfEmpty':
            operation = 'insert_if_empty'
        
        # Handle both old 'filter' format and new 'condition' format
        if 'filter' in relation:
            # Legacy format with multiple conditions
            filter_dict = relation['filter']
            
            # Process each filter condition
            for i in range(len(filter_dict['lhs'])):
                col = filter_dict['lhs'][i]
                value = filter_dict['rhs'][i]
                op = filter_dict['operation'][i]
                
                if col not in df.columns:
                    raise ValueError(f"Column '{col}' not found in dataframe when processing relation for '{col_name}'")
                
                if mask is None:
                    # First condition
                    if op == "!=":
                        mask = (df[col] != compare_type(value))
                    elif op == "<":
                        mask = (df[col] < compare_type(value))
                    elif op == ">":
                        mask = (df[col] > compare_type(value))
                    elif op == "<=":
                        mask = (df[col] <= compare_type(value))
                    elif op == ">=":
                        mask = (df[col] >= compare_type(value))
                    elif op.lower() == "==":
                        mask = (df[col] == compare_type(value))
                    else:
                        mask = (df[col] == compare_type(value))
                else:
                    # Subsequent conditions
                    if op == "!=":
                        temp = (df[col] != compare_type(value))
                    elif op == ">":
                        temp = (df[col] > compare_type(value))
                    elif op == "<":
                        temp = (df[col] < compare_type(value))
                    elif op == "<=":
                        temp = (df[col] <= compare_type(value))
                    elif op == ">=":
                        temp = (df[col] >= compare_type(value))
                    elif op.lower() == "==":
                        temp = (df[col] == compare_type(value))
                    else: 
                        temp = (df[col] == compare_type(value))
                    
                    # Apply boolean operation (if we have more than one condition)
                    boolean_op = filter_dict['boolean'][i-1].lower()
                    if boolean_op == "and" or boolean_op == "&":
                        mask = mask & temp
                    elif boolean_op == "or" or boolean_op == "|":
                        mask = mask | temp
                    else:
                        raise ValueError(f"Unsupported boolean operator: {boolean_op}. Use 'and' or 'or'.")
        
        elif 'condition' in relation:
            # New format with single condition
            condition = relation['condition']
            col = condition['column_name']
            op = condition.get('operator', 'EQUAL')
            value = condition.get('value', None)
            
            logger.debug(f"Processing condition: {col} {op} {value}")
            
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in dataframe when processing relation for '{col_name}'")
            
            # Map operator names to actual operations
            if op.upper() == "EQUAL" or op.upper() == "EQ":
                mask = (df[col] == compare_type(value))
            elif op.upper() == "NOT_EQUAL" or op.upper() == "NE":
                mask = (df[col] != compare_type(value))
            elif op.upper() == "GREATER_THAN" or op.upper() == "GT":
                mask = (df[col] > compare_type(value))
            elif op.upper() == "LESS_THAN" or op.upper() == "LT":
                mask = (df[col] < compare_type(value))
            elif op.upper() == "GREATER_THAN_EQUAL" or op.upper() == "GTE":
                mask = (df[col] >= compare_type(value))
            elif op.upper() == "LESS_THAN_EQUAL" or op.upper() == "LTE":
                mask = (df[col] <= compare_type(value))
            elif op.upper() == "NOT_NULL":
                mask = (~df[col].isnull())
            elif op.upper() == "IS_NULL":
                mask = df[col].isnull()
            else:
                raise ValueError(f"Unsupported operator: {op}")
        
        else:
            raise ValueError("No 'filter' or 'condition' found in relation")
            
        # Apply strategy with the computed mask
        strategy_module_path = STRATEGIES[relation['strategy']['name']]
        strategy_module = load_strategy_module(strategy_module_path)
        strategy_function = getattr(strategy_module, LOGICAL_MAPPING[relation['strategy']['name']])
        
        # Check if this is an intermediate column
        intermediate = relation.get('intermediate', False)
        
        # Apply transformation if specified
        transform_code = None
        if 'transform' in relation and 'code' in relation['transform']:
            transform_code = relation['transform']['code']
        
        params = args_to_dict(
            params=relation['strategy'].get('params', {}), 
            df=df,
            col_name=col_name, 
            rows=rows, 
            operation=operation, 
            debug=relation.get("debug", False), 
            mask=mask,
            intermediate=intermediate,
            transform=transform_code
        )
        
        df = strategy_function(**params)
        
    except Exception as e:
        logger.error(f"Error applying relation to column {col_name}: {str(e)}")
        raise
        
    return df