export interface StrategyParameter {
  name: string;
  type: 'str' | 'int' | 'bool' | 'list[string]' | 'list[number]' | 'select'; // Added 'select' for dropdowns
  label: string;
  default?: any;
  required?: boolean;
  options?: string[]; // For type 'select'
  placeholder?: string;
  description?: string; // Optional description for tooltip or helper text
}

export interface StrategySchema {
  strategy_name: string;
  description: string;
  parameters: StrategyParameter[];
}

// Example of what the API might return for /get_strategy_schemas
export interface StrategyCollection {
  [key: string]: StrategySchema;
}
