import React from 'react';
import { Clock } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';

interface TimeRangeFormProps {
  columnId: string;
  currentParams: Record<string, any>;
  onParamsChange: (columnId: string, paramName: string, value: any) => void;
}

export const TimeRangeForm: React.FC<TimeRangeFormProps> = ({
  columnId,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(columnId, paramName, value);
  };

  const formatOptions = [
    { value: 'HH:mm:ss', label: '24-hour (HH:mm:ss)' },
    { value: 'hh:mm:ss a', label: '12-hour (hh:mm:ss AM/PM)' },
    { value: 'HH:mm', label: '24-hour (HH:mm)' },
    { value: 'hh:mm a', label: '12-hour (hh:mm AM/PM)' },
  ];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <FormGroup label="Start Time" htmlFor={`${columnId}-start_time`} required>
          <TextInput
            id={`${columnId}-start_time`}
            name="start_time"
            type="text"
            pattern="([01]?[0-9]|2[0-3]):[0-5][0-9]"
            placeholder="HH:mm"
            value={currentParams.start_time ?? '00:00'}
            onChange={(e) => handleInputChange('start_time', e.target.value)}
            required
          />
        </FormGroup>

        <FormGroup label="End Time" htmlFor={`${columnId}-end_time`} required>
          <TextInput
            id={`${columnId}-end_time`}
            name="end_time"
            type="text"
            pattern="([01]?[0-9]|2[0-3]):[0-5][0-9]"
            placeholder="HH:mm"
            value={currentParams.end_time ?? '23:59'}
            onChange={(e) => handleInputChange('end_time', e.target.value)}
            required
          />
        </FormGroup>
      </div>

      <FormGroup label="Time Format" htmlFor={`${columnId}-format`} required>
        <SelectInput
          id={`${columnId}-format`}
          name="format"
          value={currentParams.format ?? 'HH:mm:ss'}
          onChange={(e) => handleInputChange('format', e.target.value)}
          options={formatOptions}
          required
        />
      </FormGroup>

      <FormGroup label="Step (minutes)" htmlFor={`${columnId}-step`}>
        <TextInput
          id={`${columnId}-step`}
          name="step"
          type="number"
          min="1"
          value={currentParams.step ?? 1}
          onChange={(e) => handleInputChange('step', parseInt(e.target.value))}
        />
      </FormGroup>

      <div className="p-3 bg-gray-50 rounded-md">
        <p className="text-sm text-gray-600">
          Example output: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}; 