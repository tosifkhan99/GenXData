import React from 'react';
import { Hash } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';

interface PatternFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const PatternForm: React.FC<PatternFormProps> = ({
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
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Pattern Parameters</h4>
      </div>

      <FormGroup label="Regex Pattern" htmlFor={`config-${configIndex}-regex`} required>
        <TextInput
          id={`config-${configIndex}-regex`}
          name="regex"
          value={currentParams.regex ?? ''}
          onChange={(e) => handleInputChange('regex', e.target.value)}
          placeholder="e.g., [A-Z]{2}[0-9]{3}"
          required
        />
      </FormGroup>

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Pattern Examples:</h5>
        <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
          <li>• <code>[A-Z]{`{2}`}[0-9]{`{3}`}</code> - Two uppercase letters followed by three digits (e.g., AB123)</li>
          <li>• <code>\+1-[0-9]{`{3}`}-[0-9]{`{3}`}-[0-9]{`{4}`}</code> - US phone number format</li>
          <li>• <code>[a-z]{`{3,8}`}\.[a-z]{`{2,4}`}</code> - Simple domain name pattern</li>
          <li>• <code>[A-Z][a-z]{`{5,10}`}_[0-9]{`{2}`}</code> - Username with underscore and numbers</li>
        </ul>
      </div>
    </div>
  );
};
