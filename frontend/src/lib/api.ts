import type { StrategyCollection, StrategySchema } from '../types/strategy';

// Environment-based API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? 'http://localhost:8000' : '');

// For Docker deployment, use relative URLs in production
const getApiUrl = (endpoint: string) => {
  if (import.meta.env.DEV) {
    return `${API_BASE_URL}${endpoint}`;
  }
  // In production (Docker), use relative URLs
  return endpoint;
};

// Define parameters for each strategy type
const strategyParameters: Record<string, StrategySchema['parameters']> = {
  series: [
    {
      name: 'start',
      type: 'int',
      label: 'Start Value',
      description: 'The starting value for the series',
      required: true,
      default: 1
    },
    {
      name: 'step',
      type: 'int',
      label: 'Step Value',
      description: 'The increment between values',
      required: true,
      default: 1
    }
  ],
  random_name: [
    {
      name: 'gender',
      type: 'select',
      label: 'Gender',
      description: 'The gender for name generation',
      required: false,
      options: ['male', 'female', 'any']
    }
  ],
  distributed_number_range: [
    {
      name: 'start',
      type: 'int',
      label: 'Start Value',
      description: 'The minimum value in the range',
      required: true
    },
    {
      name: 'end',
      type: 'int',
      label: 'End Value',
      description: 'The maximum value in the range',
      required: true
    },
    {
      name: 'distribution',
      type: 'str',
      label: 'Distribution',
      description: 'The distribution type (e.g., uniform, normal)',
      required: true
    }
  ],
  concat: [
    {
      name: 'columns',
      type: 'list[string]',
      label: 'Columns',
      description: 'The columns to concatenate',
      required: true
    },
    {
      name: 'separator',
      type: 'str',
      label: 'Separator',
      description: 'The separator between concatenated values',
      required: false,
      default: ''
    }
  ],
  pattern: [
    {
      name: 'regex',
      type: 'str',
      label: 'Regular Expression',
      description: 'The regex pattern to match',
      required: true
    }
  ],
  distributed_choice: [
    {
      name: 'choices',
      type: 'list[string]',
      label: 'Choices',
      description: 'The possible values to choose from',
      required: true
    },
    {
      name: 'distribution',
      type: 'list[number]',
      label: 'Distribution',
      description: 'The probability distribution for each choice',
      required: true
    }
  ]
};

export const getStrategySchemas = async (): Promise<StrategyCollection> => {
  try {
    const response = await fetch(getApiUrl('/get_strategy_schemas'));
    if (!response.ok) {
      console.error(`HTTP error fetching strategy schemas: ${response.status}`, await response.text());
      throw new Error(`Error fetching strategy schemas: ${response.statusText}`);
    }
    const data = await response.json();


    // Transform the backend response into the expected format
    const transformedStrategies: StrategyCollection = {};

    Object.entries(data.strategies).forEach(([strategyName, description]) => {
      transformedStrategies[strategyName] = {
        strategy_name: strategyName,
        description: description as string,
        parameters: strategyParameters[strategyName] || []
      };
    });


    return transformedStrategies;
  } catch (error) {
    console.error('Failed to get strategy schemas:', error);
    // Return a default or empty state to prevent breaking the UI
    // The UI should handle the case where strategies are empty.
    return {}; // Return empty object for StrategyCollection
  }
};
