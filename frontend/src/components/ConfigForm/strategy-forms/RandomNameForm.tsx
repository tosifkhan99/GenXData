import React from 'react';
import { User } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import SelectInput from '@/components/ui/forms/SelectInput';

interface RandomNameFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const RandomNameForm: React.FC<RandomNameFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(configIndex, paramName, value);
  };

  const nameTypeOptions = [
    { value: 'first', label: 'First Name Only' },
    { value: 'last', label: 'Last Name Only' },
    { value: 'full', label: 'Full Name (First + Last)' },
  ];

  const genderOptions = [
    { value: 'any', label: 'Any' },
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
  ];

  const caseOptions = [
    { value: 'title', label: 'Title Case' },
    { value: 'upper', label: 'UPPERCASE' },
    { value: 'lower', label: 'lowercase' },
  ];

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <User className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Random Name Parameters</h4>
      </div>

      <FormGroup label="Name Type" htmlFor={`config-${configIndex}-name_type`} required>
        <SelectInput
          id={`config-${configIndex}-name_type`}
          name="name_type"
          value={currentParams.name_type ?? 'full'}
          onChange={(e) => handleInputChange('name_type', e.target.value)}
          options={nameTypeOptions}
          required
        />
      </FormGroup>

      <FormGroup label="Gender" htmlFor={`config-${configIndex}-gender`} required>
        <SelectInput
          id={`config-${configIndex}-gender`}
          name="gender"
          value={currentParams.gender ?? 'any'}
          onChange={(e) => handleInputChange('gender', e.target.value)}
          options={genderOptions}
          placeholder="Select gender"
          required
        />
      </FormGroup>

      <FormGroup label="Case" htmlFor={`config-${configIndex}-case`} required>
        <SelectInput
          id={`config-${configIndex}-case`}
          name="case"
          value={currentParams.case ?? 'title'}
          onChange={(e) => handleInputChange('case', e.target.value)}
          options={caseOptions}
          placeholder="Select case"
          required
        />
      </FormGroup>

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Name Examples:</h5>
        <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
          <li>• <strong>Full Name (Title Case):</strong> John Smith</li>
          <li>• <strong>First Name (UPPERCASE):</strong> JOHN</li>
          <li>• <strong>Last Name (lowercase):</strong> smith</li>
          <li>• <strong>Female Full Name:</strong> Sarah Johnson</li>
          <li>• <strong>Male Full Name:</strong> Michael Brown</li>
        </ul>
      </div>

      <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Generates random names from a built-in database of common names.
        </p>
      </div>
    </div>
  );
};
