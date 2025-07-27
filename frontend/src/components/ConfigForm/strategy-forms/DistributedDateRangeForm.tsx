import React from 'react';
import { Calendar } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';
import { Button } from '@/components/ui/button';
import { Plus, Trash2 } from 'lucide-react';

interface DateRange {
  start_date: string;
  end_date: string;
  format: string;
  output_format: string;
  distribution: number;
}

interface DistributedDateRangeFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const DistributedDateRangeForm: React.FC<DistributedDateRangeFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  const getRangesArray = (): DateRange[] => {
    if (currentParams.ranges && Array.isArray(currentParams.ranges)) {
      return currentParams.ranges.map((range: any) => ({
        start_date: range.start_date || '2020-01-01',
        end_date: range.end_date || '2020-12-31',
        format: range.format || '%Y-%m-%d',
        output_format: range.output_format || '%Y-%m-%d',
        distribution: range.distribution || 0
      }));
    }
    return [];
  };

  const updateRanges = (ranges: DateRange[]) => {
    onParamsChange(configIndex, 'ranges', ranges);
  };

  const ranges = getRangesArray();

  const handleAddRange = () => {
    const newRanges = [...ranges, {
      start_date: '2020-01-01',
      end_date: '2020-12-31',
      format: '%Y-%m-%d',
      output_format: '%Y-%m-%d',
      distribution: 0
    }];
    updateRanges(newRanges);
  };

  const handleRemoveRange = (index: number) => {
    const newRanges = ranges.filter((_, i) => i !== index);
    updateRanges(newRanges);
  };

  const handleRangeChange = (index: number, field: keyof DateRange, value: string | number) => {
    const newRanges = ranges.map((range, i) => {
      if (i === index) {
        return { ...range, [field]: value };
      }
      return range;
    });
    updateRanges(newRanges);
  };

  const formatOptions = [
    { value: '%Y-%m-%d', label: 'YYYY-MM-DD' },
    { value: '%d/%m/%Y', label: 'DD/MM/YYYY' },
    { value: '%m/%d/%Y', label: 'MM/DD/YYYY' },
    { value: '%Y-%m-%d %H:%M:%S', label: 'YYYY-MM-DD HH:MM:SS' },
    { value: '%d-%b-%Y', label: 'DD-MMM-YYYY' },
    { value: '%B %d, %Y', label: 'Month DD, YYYY' },
  ];

  const totalDistribution = ranges.reduce((sum, range) => sum + (range.distribution || 0), 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-gray-500" />
          <h5 className="text-sm font-medium text-gray-700">Date Ranges</h5>
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
            <h6 className="text-sm font-medium text-gray-600">Date Range {index + 1}</h6>
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
            <FormGroup label="Start Date" htmlFor={`config-${configIndex}-range-${index}-start_date`}>
              <TextInput
                id={`config-${configIndex}-range-${index}-start_date`}
                name={`range-${index}-start_date`}
                type="text"
                placeholder="2020-01-01"
                value={range.start_date}
                onChange={(e) => handleRangeChange(index, 'start_date', e.target.value)}
                required
              />
            </FormGroup>

            <FormGroup label="End Date" htmlFor={`config-${configIndex}-range-${index}-end_date`}>
              <TextInput
                id={`config-${configIndex}-range-${index}-end_date`}
                name={`range-${index}-end_date`}
                type="text"
                placeholder="2020-12-31"
                value={range.end_date}
                onChange={(e) => handleRangeChange(index, 'end_date', e.target.value)}
                required
              />
            </FormGroup>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormGroup label="Input Format" htmlFor={`config-${configIndex}-range-${index}-format`}>
              <SelectInput
                id={`config-${configIndex}-range-${index}-format`}
                name={`range-${index}-format`}
                value={range.format}
                onChange={(e) => handleRangeChange(index, 'format', e.target.value)}
                options={formatOptions}
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Format of the input start/end dates
              </p>
            </FormGroup>

            <FormGroup label="Output Format" htmlFor={`config-${configIndex}-range-${index}-output_format`}>
              <SelectInput
                id={`config-${configIndex}-range-${index}-output_format`}
                name={`range-${index}-output_format`}
                value={range.output_format}
                onChange={(e) => handleRangeChange(index, 'output_format', e.target.value)}
                options={formatOptions}
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Format of the generated dates
              </p>
            </FormGroup>
          </div>

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
          Add date ranges to specify date distributions for different time periods.
        </p>
      )}

      <div className="p-4 bg-blue-50 rounded-md">
        <h5 className="text-sm font-medium text-blue-700 mb-2">Date Format Examples:</h5>
        <ul className="text-xs text-blue-600 space-y-1">
          <li>• <code>%Y-%m-%d</code> - 2024-03-15</li>
          <li>• <code>%d/%m/%Y</code> - 15/03/2024</li>
          <li>• <code>%m/%d/%Y</code> - 03/15/2024</li>
          <li>• <code>%Y-%m-%d %H:%M:%S</code> - 2024-03-15 14:30:00</li>
          <li>• <code>%d-%b-%Y</code> - 15-Mar-2024</li>
          <li>• <code>%B %d, %Y</code> - March 15, 2024</li>
        </ul>
        <div className="mt-2 pt-2 border-t border-blue-200">
          <p className="text-xs text-blue-600">
            <strong>Use Cases:</strong> Historical events, generational data, seasonal trends, quarterly analysis
          </p>
        </div>
      </div>
    </div>
  );
};
