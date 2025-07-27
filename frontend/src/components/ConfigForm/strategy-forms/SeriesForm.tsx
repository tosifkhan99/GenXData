import React from 'react';
import { Hash } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';

interface SeriesFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const SeriesForm: React.FC<SeriesFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(configIndex, paramName, value);
  };

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <Hash className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Series Parameters</h4>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Start Value" htmlFor={`config-${configIndex}-start`} required>
          <TextInput
            id={`config-${configIndex}-start`}
            name="start"
            type="number"
            value={currentParams.start ?? 1}
            onChange={(e) => handleInputChange('start', parseInt(e.target.value))}
            required
          />
        </FormGroup>

        <FormGroup label="Step" htmlFor={`config-${configIndex}-step`} required>
          <TextInput
            id={`config-${configIndex}-step`}
            name="step"
            type="number"
            value={currentParams.step ?? 1}
            onChange={(e) => handleInputChange('step', parseInt(e.target.value))}
            required
          />
        </FormGroup>
      </div>

      <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Generates sequential numbers starting from <strong>{currentParams.start ?? 1}</strong> with steps of <strong>{currentParams.step ?? 1}</strong>
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
          Example: {currentParams.start ?? 1}, {(currentParams.start ?? 1) + (currentParams.step ?? 1)}, {(currentParams.start ?? 1) + 2 * (currentParams.step ?? 1)}, ...
        </p>
      </div>
    </div>
  );
};
