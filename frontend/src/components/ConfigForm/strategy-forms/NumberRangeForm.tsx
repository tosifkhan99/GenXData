import React from 'react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import CheckboxInput from '@/components/ui/forms/CheckboxInput';

interface NumberRangeFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const NumberRangeForm: React.FC<NumberRangeFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(configIndex, paramName, value);
  };

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Number Range Parameters</h4>

      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Start Value" htmlFor={`config-${configIndex}-start`} required>
          <TextInput
            id={`config-${configIndex}-start`}
            name="start"
            type="number"
            step="any"
            value={currentParams.start ?? 0}
            onChange={(e) => handleInputChange('start', parseFloat(e.target.value))}
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
            onChange={(e) => handleInputChange('end', parseFloat(e.target.value))}
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
            min="0.001"
            value={currentParams.step ?? 1}
            onChange={(e) => handleInputChange('step', parseFloat(e.target.value))}
          />
        </FormGroup>

        <FormGroup label="Decimal Precision" htmlFor={`config-${configIndex}-precision`}>
          <TextInput
            id={`config-${configIndex}-precision`}
            name="precision"
            type="number"
            min="0"
            max="10"
            value={currentParams.precision ?? 0}
            onChange={(e) => handleInputChange('precision', parseInt(e.target.value))}
          />
        </FormGroup>
      </div>

      <CheckboxInput
        id={`config-${configIndex}-unique`}
        name="unique"
        label="Generate unique values only"
        checked={currentParams.unique ?? false}
        onChange={(e) => handleInputChange('unique', e.target.checked)}
      />

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Configuration Notes:</h5>
        <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
          <li>• Step determines the interval between possible values</li>
          <li>• Precision controls decimal places in the output</li>
          <li>• Unique option ensures no duplicate values (may affect performance)</li>
          <li>• End value is exclusive (not included in the range)</li>
        </ul>
      </div>
    </div>
  );
};
