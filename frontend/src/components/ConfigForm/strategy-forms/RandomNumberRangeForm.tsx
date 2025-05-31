import React from 'react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';

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

  const distributionOptions = [
    { value: 'uniform', label: 'Uniform (Equal probability)' },
    { value: 'normal', label: 'Normal (Bell curve)' },
    { value: 'exponential', label: 'Exponential' },
  ];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Minimum Value" htmlFor={`config-${configIndex}-min_value`} required>
          <TextInput
            id={`config-${configIndex}-min_value`}
            name="min_value"
            type="number"
            value={currentParams.min_value ?? currentParams.min ?? ''}
            onChange={(e) => handleInputChange('min_value', parseFloat(e.target.value))}
            required
          />
        </FormGroup>

        <FormGroup label="Maximum Value" htmlFor={`config-${configIndex}-max_value`} required>
          <TextInput
            id={`config-${configIndex}-max_value`}
            name="max_value"
            type="number"
            value={currentParams.max_value ?? currentParams.max ?? ''}
            onChange={(e) => handleInputChange('max_value', parseFloat(e.target.value))}
            required
          />
        </FormGroup>
      </div>

      <FormGroup label="Distribution Type" htmlFor={`config-${configIndex}-distribution`} required>
        <SelectInput
          id={`config-${configIndex}-distribution`}
          name="distribution"
          value={currentParams.distribution ?? 'uniform'}
          onChange={(e) => handleInputChange('distribution', e.target.value)}
          options={distributionOptions}
          required
        />
      </FormGroup>

      {currentParams.distribution === 'normal' && (
        <div className="grid grid-cols-2 gap-4">
          <FormGroup label="Mean" htmlFor={`config-${configIndex}-mean`} required>
            <TextInput
              id={`config-${configIndex}-mean`}
              name="mean"
              type="number"
              value={currentParams.mean ?? ''}
              onChange={(e) => handleInputChange('mean', parseFloat(e.target.value))}
              required
            />
          </FormGroup>

          <FormGroup label="Standard Deviation" htmlFor={`config-${configIndex}-std_dev`} required>
            <TextInput
              id={`config-${configIndex}-std_dev`}
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
        <FormGroup label="Rate Parameter (λ)" htmlFor={`config-${configIndex}-rate`} required>
          <TextInput
            id={`config-${configIndex}-rate`}
            name="rate"
            type="number"
            min="0"
            step="0.1"
            value={currentParams.rate ?? ''}
            onChange={(e) => handleInputChange('rate', parseFloat(e.target.value))}
            required
          />
        </FormGroup>
      )}

      <FormGroup label="Decimal Places" htmlFor={`config-${configIndex}-decimal_places`}>
        <TextInput
          id={`config-${configIndex}-decimal_places`}
          name="decimal_places"
          type="number"
          min="0"
          max="10"
          value={currentParams.decimal_places ?? 0}
          onChange={(e) => handleInputChange('decimal_places', parseInt(e.target.value))}
        />
      </FormGroup>
    </div>
  );
}; 