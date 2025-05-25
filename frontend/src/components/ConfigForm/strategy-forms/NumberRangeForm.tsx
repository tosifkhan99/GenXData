import React from 'react';
import { Hash } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';

interface NumberRangeFormProps {
  columnId: string;
  currentParams: Record<string, any>;
  onParamsChange: (columnId: string, paramName: string, value: any) => void;
}

export const NumberRangeForm: React.FC<NumberRangeFormProps> = ({
  columnId,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(columnId, paramName, value);
  };

  const distributionOptions = [
    { value: 'uniform', label: 'Uniform' },
    { value: 'normal', label: 'Normal (Gaussian)' },
    { value: 'exponential', label: 'Exponential' },
  ];

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <Hash className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Number Range Parameters</h4>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Start Value" htmlFor={`${columnId}-start`} required>
          <TextInput
            id={`${columnId}-start`}
            name="start"
            type="number"
            value={currentParams.start ?? ''}
            onChange={(e) => handleInputChange('start', parseFloat(e.target.value))}
            required
          />
        </FormGroup>

        <FormGroup label="End Value" htmlFor={`${columnId}-end`} required>
          <TextInput
            id={`${columnId}-end`}
            name="end"
            type="number"
            value={currentParams.end ?? ''}
            onChange={(e) => handleInputChange('end', parseFloat(e.target.value))}
            required
          />
        </FormGroup>
      </div>

      <FormGroup label="Distribution" htmlFor={`${columnId}-distribution`} required>
        <SelectInput
          id={`${columnId}-distribution`}
          name="distribution"
          value={currentParams.distribution ?? 'uniform'}
          onChange={(e) => handleInputChange('distribution', e.target.value)}
          options={distributionOptions}
          placeholder="Select distribution type"
          required
        />
      </FormGroup>

      {currentParams.distribution === 'normal' && (
        <div className="grid grid-cols-2 gap-4">
          <FormGroup label="Mean" htmlFor={`${columnId}-mean`} required>
            <TextInput
              id={`${columnId}-mean`}
              name="mean"
              type="number"
              value={currentParams.mean ?? ''}
              onChange={(e) => handleInputChange('mean', parseFloat(e.target.value))}
              required
            />
          </FormGroup>

          <FormGroup label="Standard Deviation" htmlFor={`${columnId}-std_dev`} required>
            <TextInput
              id={`${columnId}-std_dev`}
              name="std_dev"
              type="number"
              min="0"
              step="0.1"
              value={currentParams.std_dev ?? ''}
              onChange={(e) => handleInputChange('std_dev', parseFloat(e.target.value))}
              required
            />
          </FormGroup>
        </div>
      )}

      {currentParams.distribution === 'exponential' && (
        <FormGroup label="Rate Parameter (λ)" htmlFor={`${columnId}-rate`} required>
          <TextInput
            id={`${columnId}-rate`}
            name="rate"
            type="number"
            min="0"
            step="0.1"
            value={currentParams.rate ?? ''}
            onChange={(e) => handleInputChange('rate', parseFloat(e.target.value))}
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Higher values create a steeper exponential curve
          </p>
        </FormGroup>
      )}

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Distribution Types:</h5>
        <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
          <li>• <strong>Uniform:</strong> Equal probability for all values in range</li>
          <li>• <strong>Normal:</strong> Bell-shaped distribution around the mean</li>
          <li>• <strong>Exponential:</strong> Decreasing probability as values increase</li>
        </ul>
      </div>
    </div>
  );
}; 