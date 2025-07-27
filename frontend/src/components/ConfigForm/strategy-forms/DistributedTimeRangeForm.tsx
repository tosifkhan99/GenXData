import React from 'react';
import { Clock } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';
import { Button } from '@/components/ui/button';
import { Plus, Trash2 } from 'lucide-react';

interface TimeRange {
  start: string;
  end: string;
  format: string;
  distribution: number;
}

interface DistributedTimeRangeFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const DistributedTimeRangeForm: React.FC<DistributedTimeRangeFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const getRangesArray = (): TimeRange[] => {
    if (currentParams.ranges && Array.isArray(currentParams.ranges)) {
      return currentParams.ranges.map((range: any) => ({
        start: range.start || '00:00:00',
        end: range.end || '23:59:59',
        format: range.format || '%H:%M:%S',
        distribution: range.distribution || 0
      }));
    }
    return [];
  };

  const updateRanges = (ranges: TimeRange[]) => {
    onParamsChange(configIndex, 'ranges', ranges);
  };

  const ranges = getRangesArray();

  const handleAddRange = () => {
    const newRanges = [...ranges, {
      start: '00:00:00',
      end: '23:59:59',
      format: '%H:%M:%S',
      distribution: 0
    }];
    updateRanges(newRanges);
  };

  const handleRemoveRange = (index: number) => {
    const newRanges = ranges.filter((_, i) => i !== index);
    updateRanges(newRanges);
  };

  const handleRangeChange = (index: number, field: keyof TimeRange, value: string | number) => {
    const newRanges = ranges.map((range, i) => {
      if (i === index) {
        return { ...range, [field]: value };
      }
      return range;
    });
    updateRanges(newRanges);
  };

  const formatOptions = [
    { value: '%H:%M:%S', label: '24-hour (HH:MM:SS)' },
    { value: '%I:%M:%S %p', label: '12-hour (HH:MM:SS AM/PM)' },
    { value: '%H:%M', label: '24-hour (HH:MM)' },
    { value: '%I:%M %p', label: '12-hour (HH:MM AM/PM)' },
  ];

  const totalDistribution = ranges.reduce((sum, range) => sum + (range.distribution || 0), 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-500" />
          <h5 className="text-sm font-medium text-gray-700">Time Ranges</h5>
        </div>
        <Button
          type="button"
          onClick={handleAddRange}
          variant="outline"
          size="sm"
          className="flex items-center gap-1"
        >
          <Plus className="w-4 h-4" />
          Add Range
        </Button>
      </div>

      {ranges.map((range, index) => (
        <div key={index} className="p-4 border border-gray-200 rounded-md space-y-3">
          <div className="flex justify-between items-center">
            <h6 className="text-sm font-medium text-gray-600">Time Range {index + 1}</h6>
            <Button
              type="button"
              onClick={() => handleRemoveRange(index)}
              variant="ghost"
              size="sm"
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormGroup label="Start Time" htmlFor={`config-${configIndex}-range-${index}-start`}>
              <TextInput
                id={`config-${configIndex}-range-${index}-start`}
                name={`range-${index}-start`}
                type="text"
                placeholder="00:00:00"
                value={range.start}
                onChange={(e) => handleRangeChange(index, 'start', e.target.value)}
                required
              />
            </FormGroup>

            <FormGroup label="End Time" htmlFor={`config-${configIndex}-range-${index}-end`}>
              <TextInput
                id={`config-${configIndex}-range-${index}-end`}
                name={`range-${index}-end`}
                type="text"
                placeholder="23:59:59"
                value={range.end}
                onChange={(e) => handleRangeChange(index, 'end', e.target.value)}
                required
              />
            </FormGroup>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormGroup label="Time Format" htmlFor={`config-${configIndex}-range-${index}-format`}>
              <SelectInput
                id={`config-${configIndex}-range-${index}-format`}
                name={`range-${index}-format`}
                value={range.format}
                onChange={(e) => handleRangeChange(index, 'format', e.target.value)}
                options={formatOptions}
                required
              />
            </FormGroup>

            <FormGroup label="Distribution %" htmlFor={`config-${configIndex}-range-${index}-distribution`}>
              <TextInput
                id={`config-${configIndex}-range-${index}-distribution`}
                name={`range-${index}-distribution`}
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={range.distribution}
                onChange={(e) => handleRangeChange(index, 'distribution', parseFloat(e.target.value))}
                required
              />
            </FormGroup>
          </div>

          <div className="p-2 bg-gray-50 rounded-md">
            <p className="text-xs text-gray-600">
              <strong>Overnight ranges supported:</strong> For ranges that cross midnight (e.g., 22:00:00 to 06:00:00),
              the system will generate times from 22:00 to 23:59, then from 00:00 to 06:00.
            </p>
          </div>
        </div>
      ))}

      {ranges.length > 0 && (
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <p className="text-sm text-gray-600">
            Total Distribution: {totalDistribution.toFixed(1)}%
            {totalDistribution !== 100 && (
              <span className="text-red-500 ml-2">
                (Should equal 100%)
              </span>
            )}
          </p>
        </div>
      )}

      {ranges.length === 0 && (
        <p className="text-sm text-gray-500 text-center py-4">
          Add time ranges to specify time distributions. Supports overnight ranges (e.g., 22:00 to 06:00).
        </p>
      )}

      <div className="p-4 bg-blue-50 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 mb-2">Time Format Examples:</h5>
        <ul className="text-xs text-blue-600 space-y-1">
          <li>• <code>%H:%M:%S</code> - 14:30:25 (24-hour with seconds)</li>
          <li>• <code>%I:%M:%S %p</code> - 02:30:25 PM (12-hour with seconds)</li>
          <li>• <code>%H:%M</code> - 14:30 (24-hour without seconds)</li>
          <li>• <code>%I:%M %p</code> - 02:30 PM (12-hour without seconds)</li>
        </ul>
      </div>
    </div>
  );
};
