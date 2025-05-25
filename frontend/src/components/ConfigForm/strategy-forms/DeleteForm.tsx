import React from 'react';
import { Trash2 } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

interface DeleteCondition {
  field: string;
  operator: string;
  value: string;
}

interface DeleteFormProps {
  columnId: string;
  currentParams: Record<string, any>;
  onParamsChange: (columnId: string, paramName: string, value: any) => void;
}

export const DeleteForm: React.FC<DeleteFormProps> = ({
  columnId,
  currentParams,
  onParamsChange,
}) => {
  const conditions: DeleteCondition[] = currentParams.conditions || [];

  const handleAddCondition = () => {
    const newConditions = [...conditions, { field: '', operator: 'equals', value: '' }];
    onParamsChange(columnId, 'conditions', newConditions);
  };

  const handleRemoveCondition = (index: number) => {
    const newConditions = conditions.filter((_, i) => i !== index);
    onParamsChange(columnId, 'conditions', newConditions);
  };

  const handleConditionChange = (index: number, field: keyof DeleteCondition, value: string) => {
    const newConditions = conditions.map((condition, i) => {
      if (i === index) {
        return { ...condition, [field]: value };
      }
      return condition;
    });
    onParamsChange(columnId, 'conditions', newConditions);
  };

  const operatorOptions = [
    { value: 'equals', label: 'Equals' },
    { value: 'not_equals', label: 'Not Equals' },
    { value: 'contains', label: 'Contains' },
    { value: 'not_contains', label: 'Not Contains' },
    { value: 'starts_with', label: 'Starts With' },
    { value: 'ends_with', label: 'Ends With' },
    { value: 'greater_than', label: 'Greater Than' },
    { value: 'less_than', label: 'Less Than' },
    { value: 'is_null', label: 'Is Null' },
    { value: 'is_not_null', label: 'Is Not Null' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h5 className="text-sm font-medium text-gray-700">Delete Conditions</h5>
        <Button
          type="button"
          onClick={handleAddCondition}
          variant="outline"
          size="sm"
          className="flex items-center gap-1"
        >
          <Plus className="w-4 h-4" />
          Add Condition
        </Button>
      </div>

      {conditions.map((condition, index) => (
        <div key={index} className="p-4 border border-gray-200 rounded-md space-y-3">
          <div className="flex justify-between items-center">
            <h6 className="text-sm font-medium text-gray-600">Condition {index + 1}</h6>
            <Button
              type="button"
              onClick={() => handleRemoveCondition(index)}
              variant="ghost"
              size="sm"
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <FormGroup label="Field" htmlFor={`${columnId}-condition-${index}-field`} required>
              <TextInput
                id={`${columnId}-condition-${index}-field`}
                name={`condition-${index}-field`}
                value={condition.field}
                onChange={(e) => handleConditionChange(index, 'field', e.target.value)}
                placeholder="Column name"
                required
              />
            </FormGroup>

            <FormGroup label="Operator" htmlFor={`${columnId}-condition-${index}-operator`} required>
              <SelectInput
                id={`${columnId}-condition-${index}-operator`}
                name={`condition-${index}-operator`}
                value={condition.operator}
                onChange={(e) => handleConditionChange(index, 'operator', e.target.value)}
                options={operatorOptions}
                required
              />
            </FormGroup>

            {!['is_null', 'is_not_null'].includes(condition.operator) && (
              <FormGroup label="Value" htmlFor={`${columnId}-condition-${index}-value`} required>
                <TextInput
                  id={`${columnId}-condition-${index}-value`}
                  name={`condition-${index}-value`}
                  value={condition.value}
                  onChange={(e) => handleConditionChange(index, 'value', e.target.value)}
                  placeholder="Value to compare"
                  required
                />
              </FormGroup>
            )}
          </div>
        </div>
      ))}

      {conditions.length === 0 && (
        <p className="text-sm text-gray-500 text-center py-4">
          Add conditions to specify when values should be deleted
        </p>
      )}

      <div className="p-3 bg-gray-50 rounded-md">
        <p className="text-sm text-gray-600">
          Values will be deleted when ALL conditions are met. Leave empty to delete all values.
        </p>
      </div>
    </div>
  );
}; 