import React from 'react';
import { Calendar } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';

interface DateGeneratorFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const DateGeneratorForm: React.FC<DateGeneratorFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(configIndex, paramName, value);
  };

  const formatOptions = [
    { value: '%Y-%m-%d', label: 'YYYY-MM-DD' },
    { value: '%d/%m/%Y', label: 'DD/MM/YYYY' },
    { value: '%m/%d/%Y', label: 'MM/DD/YYYY' },
    { value: '%Y-%m-%d %H:%M:%S', label: 'YYYY-MM-DD HH:MM:SS' },
    { value: '%d-%b-%Y', label: 'DD-MMM-YYYY' },
    { value: '%B %d, %Y', label: 'Month DD, YYYY' },
  ];

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <Calendar className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Date Generator Parameters</h4>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Start Date" htmlFor={`config-${configIndex}-start_date`} required>
          <TextInput
            id={`config-${configIndex}-start_date`}
            name="start_date"
            type="text"
            pattern="\d{4}-\d{2}-\d{2}"
            placeholder="YYYY-MM-DD"
            value={currentParams.start_date ?? ''}
            onChange={(e) => handleInputChange('start_date', e.target.value)}
            required
          />
        </FormGroup>

        <FormGroup label="End Date" htmlFor={`config-${configIndex}-end_date`} required>
          <TextInput
            id={`config-${configIndex}-end_date`}
            name="end_date"
            type="text"
            pattern="\d{4}-\d{2}-\d{2}"
            placeholder="YYYY-MM-DD"
            value={currentParams.end_date ?? ''}
            onChange={(e) => handleInputChange('end_date', e.target.value)}
            required
          />
        </FormGroup>
      </div>

      <FormGroup label="Input Format" htmlFor={`config-${configIndex}-format`} required>
        <SelectInput
          id={`config-${configIndex}-format`}
          name="format"
          value={currentParams.format ?? '%Y-%m-%d'}
          onChange={(e) => handleInputChange('format', e.target.value)}
          options={formatOptions}
          placeholder="Select date format"
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          Format of the input dates (start and end dates)
        </p>
      </FormGroup>

      <FormGroup label="Output Format" htmlFor={`config-${configIndex}-output_format`} required>
        <SelectInput
          id={`config-${configIndex}-output_format`}
          name="output_format"
          value={currentParams.output_format ?? '%Y-%m-%d'}
          onChange={(e) => handleInputChange('output_format', e.target.value)}
          options={formatOptions}
          placeholder="Select output format"
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          Format of the generated dates
        </p>
      </FormGroup>

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Format Examples:</h5>
        <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
          <li>• <code>%Y-%m-%d</code> - 2024-03-15</li>
          <li>• <code>%d/%m/%Y</code> - 15/03/2024</li>
          <li>• <code>%m/%d/%Y</code> - 03/15/2024</li>
          <li>• <code>%Y-%m-%d %H:%M:%S</code> - 2024-03-15 14:30:00</li>
          <li>• <code>%d-%b-%Y</code> - 15-Mar-2024</li>
          <li>• <code>%B %d, %Y</code> - March 15, 2024</li>
        </ul>
      </div>
    </div>
  );
};
