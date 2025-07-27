import React from 'react';
import { Trash2 } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';

interface DeleteFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const DeleteForm: React.FC<DeleteFormProps> = ({
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
        <Trash2 className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Delete Strategy Parameters</h4>
      </div>

      <FormGroup label="Condition (Mask)" htmlFor={`config-${configIndex}-mask`} required>
        <TextInput
          id={`config-${configIndex}-mask`}
          name="mask"
          type="text"
          value={currentParams.mask ?? ''}
          onChange={(e) => handleInputChange('mask', e.target.value)}
          placeholder="e.g., column_name < 30"
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          Condition for which rows to delete (pandas query syntax)
        </p>
      </FormGroup>

      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-md">
        <h5 className="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-2">⚠️ Warning:</h5>
        <p className="text-xs text-yellow-600 dark:text-yellow-400">
          The delete strategy permanently removes data. Make sure your condition is correct before running.
        </p>
      </div>

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Example Conditions:</h5>
        <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
          <li>• <code>age &lt; 18</code> - Delete rows where age is less than 18</li>
          <li>• <code>status == "inactive"</code> - Delete inactive records</li>
          <li>• <code>score &lt;= 0</code> - Delete zero/negative scores</li>
          <li>• <code>name.str.contains("test")</code> - Delete test accounts</li>
        </ul>
      </div>
    </div>
  );
};
