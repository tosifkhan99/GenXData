import React from 'react';
import { Link2 } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';

interface ConcatFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
  availableColumns?: string[]; // List of column names that can be concatenated
}

export const ConcatForm: React.FC<ConcatFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
  availableColumns = [],
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(configIndex, paramName, value);
  };

  const columnOptions = availableColumns.map(col => ({ value: col, label: col }));

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <Link2 className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Concatenation Parameters</h4>
      </div>

      <div className="space-y-6">
        {/* Prefix */}
        <FormGroup label="Prefix" htmlFor={`config-${configIndex}-prefix`}>
          <TextInput
            id={`config-${configIndex}-prefix`}
            name="prefix"
            value={currentParams.prefix ?? ''}
            onChange={(e) => handleInputChange('prefix', e.target.value)}
            placeholder="e.g., user-"
          />
        </FormGroup>

        {/* Left-hand side column - using lhs_col for backend compatibility */}
        <FormGroup label="Left Column" htmlFor={`config-${configIndex}-lhs_col`} required>
          <SelectInput
            id={`config-${configIndex}-lhs_col`}
            name="lhs_col"
            value={currentParams.lhs_col ?? currentParams.lhs ?? ''}
            onChange={(e) => handleInputChange('lhs_col', e.target.value)}
            options={columnOptions}
            placeholder="Select left column"
            required
          />
        </FormGroup>

        {/* Separator */}
        <FormGroup label="Separator" htmlFor={`config-${configIndex}-separator`}>
          <TextInput
            id={`config-${configIndex}-separator`}
            name="separator"
            value={currentParams.separator ?? ''}
            onChange={(e) => handleInputChange('separator', e.target.value)}
            placeholder="e.g., - or _ or ."
          />
        </FormGroup>

        {/* Right-hand side column - using rhs_col for backend compatibility */}
        <FormGroup label="Right Column" htmlFor={`config-${configIndex}-rhs_col`} required>
          <SelectInput
            id={`config-${configIndex}-rhs_col`}
            name="rhs_col"
            value={currentParams.rhs_col ?? currentParams.rhs ?? ''}
            onChange={(e) => handleInputChange('rhs_col', e.target.value)}
            options={columnOptions}
            placeholder="Select right column"
            required
          />
        </FormGroup>

        {/* Suffix */}
        <FormGroup label="Suffix" htmlFor={`config-${configIndex}-suffix`}>
          <TextInput
            id={`config-${configIndex}-suffix`}
            name="suffix"
            value={currentParams.suffix ?? ''}
            onChange={(e) => handleInputChange('suffix', e.target.value)}
            placeholder="e.g., @company.com"
          />
        </FormGroup>
      </div>
    </div>
  );
};
