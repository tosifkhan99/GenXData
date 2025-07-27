import React from 'react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import { Button } from '@/components/ui/button';
import { Plus, Trash2 } from 'lucide-react';

interface Range {
  start: number;
  end: number;
  distribution: number;
}

interface DistributedNumberRangeFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const DistributedNumberRangeForm: React.FC<DistributedNumberRangeFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  // Convert between UI (min/max) and backend (start/end) formats
  const getRangesArray = (): Range[] => {
    if (currentParams.ranges && Array.isArray(currentParams.ranges)) {
      return currentParams.ranges.map((range: any) => ({
        start: range.start || range.min || 0,
        end: range.end || range.max || 100,
        distribution: range.distribution || 0
      }));
    }
    return [];
  };

  const updateRanges = (ranges: Range[]) => {
    onParamsChange(configIndex, 'ranges', ranges);
  };

  const ranges = getRangesArray();

  const handleAddRange = () => {
    const newRanges = [...ranges, { start: 0, end: 100, distribution: 0 }];
    updateRanges(newRanges);
  };

  const handleRemoveRange = (index: number) => {
    const newRanges = ranges.filter((_, i) => i !== index);
    updateRanges(newRanges);
  };

  const handleRangeChange = (index: number, field: keyof Range, value: number) => {
    const newRanges = ranges.map((range, i) => {
      if (i === index) {
        return { ...range, [field]: value };
      }
      return range;
    });
    updateRanges(newRanges);
  };

  const totalDistribution = ranges.reduce((sum, range) => sum + (range.distribution || 0), 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h5 className="text-sm font-medium text-gray-700">Number Ranges</h5>
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
            <h6 className="text-sm font-medium text-gray-600">Range {index + 1}</h6>
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

          <div className="grid grid-cols-3 gap-4">
            <FormGroup label="Start Value" htmlFor={`config-${configIndex}-range-${index}-start`}>
              <TextInput
                id={`config-${configIndex}-range-${index}-start`}
                name={`range-${index}-start`}
                type="number"
                value={range.start}
                onChange={(e) => handleRangeChange(index, 'start', parseFloat(e.target.value))}
                required
              />
            </FormGroup>

            <FormGroup label="End Value" htmlFor={`config-${configIndex}-range-${index}-end`}>
              <TextInput
                id={`config-${configIndex}-range-${index}-end`}
                name={`range-${index}-end`}
                type="number"
                value={range.end}
                onChange={(e) => handleRangeChange(index, 'end', parseFloat(e.target.value))}
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
          Add ranges to specify number distributions
        </p>
      )}
    </div>
  );
};
