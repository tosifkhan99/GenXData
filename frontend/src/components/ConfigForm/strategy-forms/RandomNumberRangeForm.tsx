import React from 'react';
import { Calculator, AlertTriangle } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import CheckboxInput from '@/components/ui/forms/CheckboxInput';

interface RandomNumberRangeFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const RandomNumberRangeForm: React.FC<RandomNumberRangeFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(configIndex, paramName, value);
  };

  // Calculate maximum possible unique values based on parameters
  const calculateMaxUniqueValues = () => {
    const start = currentParams.start ?? 0;
    const end = currentParams.end ?? 99;
    const step = currentParams.step ?? 1;
    const precision = currentParams.precision ?? 0;

    if (precision === 0) {
      // For integers
      return Math.floor((end - start) / step) + 1;
    } else {
      // For decimals, this is more complex and depends on the step size
      const range = end - start;
      return Math.floor(range / step) + 1;
    }
  };

  const maxUniqueValues = calculateMaxUniqueValues();
  const isUniqueSelected = currentParams.unique ?? false;

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <Calculator className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Random Number Range Parameters</h4>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Start Value" htmlFor={`config-${configIndex}-start`} required>
          <TextInput
            id={`config-${configIndex}-start`}
            name="start"
            type="number"
            step="any"
            value={currentParams.start ?? 0}
            onChange={(e) => handleInputChange('start', parseFloat(e.target.value) || 0)}
            placeholder="0"
            required
          />
        </FormGroup>

        <FormGroup label="End Value" htmlFor={`config-${configIndex}-end`} required>
          <TextInput
            id={`config-${configIndex}-end`}
            name="end"
            type="number"
            step="any"
            value={currentParams.end ?? 99}
            onChange={(e) => handleInputChange('end', parseFloat(e.target.value) || 99)}
            placeholder="99"
            required
          />
        </FormGroup>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Step" htmlFor={`config-${configIndex}-step`}>
          <TextInput
            id={`config-${configIndex}-step`}
            name="step"
            type="number"
            step="any"
            min="0.000001"
            value={currentParams.step ?? 1}
            onChange={(e) => handleInputChange('step', parseFloat(e.target.value) || 1)}
            placeholder="1"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Increment between possible values
          </p>
        </FormGroup>

        <FormGroup label="Precision (Decimal Places)" htmlFor={`config-${configIndex}-precision`}>
          <TextInput
            id={`config-${configIndex}-precision`}
            name="precision"
            type="number"
            min="0"
            max="10"
            value={currentParams.precision ?? 0}
            onChange={(e) => handleInputChange('precision', parseInt(e.target.value) || 0)}
            placeholder="0"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Number of decimal places to display
          </p>
        </FormGroup>
      </div>

      <FormGroup label="Unique Values" htmlFor={`config-${configIndex}-unique`}>
        <CheckboxInput
          name={`config-${configIndex}-unique`}
          checked={currentParams.unique ?? false}
          onChange={(e) => handleInputChange('unique', e.target.checked)}
          label="Generate unique values only (no duplicates)"
          labelClassName="text-gray-700 dark:text-gray-200"
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          When enabled, each generated number will be unique within the range.
          Maximum possible unique values: <strong>{maxUniqueValues}</strong>
        </p>
      </FormGroup>

      {/* Unique Values Warning */}
      {isUniqueSelected && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-4 rounded-md">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
            <div className="space-y-2">
              <h5 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                ⚠️ Unique Number Generation Warnings
              </h5>
              <div className="text-xs text-yellow-700 dark:text-yellow-300 space-y-2">
                <div>
                  <strong>Current Implementation Limitation:</strong> The backend strategy currently uses
                  <code className="bg-yellow-100 dark:bg-yellow-800 px-1 rounded">np.random.uniform()</code>
                  which does NOT enforce uniqueness - it may generate duplicates even when unique=true.
                </div>

                <div>
                  <strong>Performance Impact:</strong> True unique generation would require:
                  <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                    <li>Pre-generating all possible values</li>
                    <li>Random sampling without replacement</li>
                    <li>Memory usage proportional to range size</li>
                  </ul>
                </div>

                <div>
                  <strong>Potential Issues:</strong>
                  <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                    <li>If requesting more rows than possible unique values ({maxUniqueValues}), generation will fail</li>
                    <li>Large ranges with small steps can consume significant memory</li>
                    <li>Decimal precision affects the actual number of possible unique values</li>
                  </ul>
                </div>

                <div className="bg-yellow-100 dark:bg-yellow-800 p-2 rounded text-xs">
                  <strong>Recommendation:</strong> For guaranteed unique values, consider using:
                  <ul className="list-disc list-inside ml-2 mt-1">
                    <li><strong>SERIES_STRATEGY</strong> for sequential numbers</li>
                    <li><strong>PATTERN_STRATEGY</strong> for unique IDs</li>
                    <li>Manually verify your range supports the required number of rows</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Configuration Examples:</h5>
        <div className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
          <div><strong>Ages:</strong> start=18, end=65, step=1, precision=0</div>
          <div><strong>Prices:</strong> start=9.99, end=999.99, step=0.01, precision=2</div>
          <div><strong>Coordinates:</strong> start=-90, end=90, step=0.000001, precision=6</div>
          <div><strong>Unique IDs:</strong> start=1000, end=9999, step=1, precision=0, unique=true</div>
        </div>
      </div>
    </div>
  );
};
