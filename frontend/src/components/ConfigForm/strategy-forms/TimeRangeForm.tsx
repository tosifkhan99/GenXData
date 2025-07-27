import React from 'react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';

interface TimeRangeFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const TimeRangeForm: React.FC<TimeRangeFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const handleInputChange = (paramName: string, value: any) => {
    onParamsChange(configIndex, paramName, value);
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
        <FormGroup label="Start Time" htmlFor={`config-${configIndex}-start_time`} required>
          <TextInput
            id={`config-${configIndex}-start_time`}
            name="start_time"
            type="text"
            pattern="([01]?[0-9]|2[0-3]):[0-5][0-9]"
            placeholder="HH:mm"
            value={currentParams.start_time ?? '00:00'}
            onChange={(e) => handleInputChange('start_time', e.target.value)}
            required
          />
        </FormGroup>

        <FormGroup label="End Time" htmlFor={`config-${configIndex}-end_time`} required>
          <TextInput
            id={`config-${configIndex}-end_time`}
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

      <FormGroup label="Time Format" htmlFor={`config-${configIndex}-format`} required>
        <SelectInput
          id={`config-${configIndex}-format`}
          name="format"
          value={currentParams.format ?? 'HH:mm:ss'}
          onChange={(e) => handleInputChange('format', e.target.value)}
          options={formatOptions}
          required
        />
      </FormGroup>

      <FormGroup label="Step (minutes)" htmlFor={`config-${configIndex}-step`}>
        <TextInput
          id={`config-${configIndex}-step`}
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
