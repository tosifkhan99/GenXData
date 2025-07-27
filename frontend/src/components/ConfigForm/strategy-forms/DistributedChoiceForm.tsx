import React from 'react';
import { ListFilter } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import { Button } from '@/components/ui/button';
import { Plus, Trash2 } from 'lucide-react';

interface Choice {
  value: string;
  distribution: number;
}

interface DistributedChoiceFormProps {
  configIndex: number;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
}

export const DistributedChoiceForm: React.FC<DistributedChoiceFormProps> = ({
  configIndex,
  currentParams,
  onParamsChange,
}) => {
  // Convert backend object format to UI array format for editing
  const getChoicesArray = (): Choice[] => {
    if (currentParams.choices) {
      if (Array.isArray(currentParams.choices)) {
        return currentParams.choices;
      } else if (typeof currentParams.choices === 'object') {
        // Convert backend object format to UI array format
        return Object.entries(currentParams.choices).map(([value, distribution]) => ({
          value,
          distribution: Number(distribution)
        }));
      }
    }
    return [];
  };

  // Convert UI array format to backend object format
  const updateChoices = (choices: Choice[]) => {
    // If we have any choices that are still being edited (empty value),
    // store as array for UI purposes
    const hasEmptyChoices = choices.some(choice => choice.value === '');

    if (hasEmptyChoices) {
      // Store as array to maintain UI state during editing
      onParamsChange(configIndex, 'choices', choices);
    } else {
      // Convert to object format for backend when all choices have values
      const choicesObj: Record<string, number> = {};
      choices.forEach(choice => {
        if (choice.value.trim()) {
          choicesObj[choice.value] = choice.distribution || 0;
        }
      });
      onParamsChange(configIndex, 'choices', choicesObj);
    }
  };

  const choices = getChoicesArray();

  const handleAddChoice = () => {
    const newChoices = [...choices, { value: '', distribution: 10 }];
    updateChoices(newChoices);
  };

  const handleRemoveChoice = (index: number) => {
    const newChoices = choices.filter((_, i) => i !== index);
    updateChoices(newChoices);
  };

  const handleChoiceChange = (index: number, field: keyof Choice, value: string | number) => {
    const newChoices = choices.map((choice, i) => {
      if (i === index) {
        return { ...choice, [field]: value };
      }
      return choice;
    });
    updateChoices(newChoices);
  };

  const totalDistribution = choices.reduce((sum, choice) => sum + (choice.distribution || 0), 0);

  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <ListFilter className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        <h4 className="text-md font-semibold text-gray-700 dark:text-gray-200">Distributed Choice Parameters</h4>
      </div>

      <div className="space-y-4">
        {choices.map((choice, index) => (
          <div key={index} className="p-4 border border-gray-200 dark:border-gray-700 rounded-md space-y-4">
            <div className="flex justify-between items-center">
              <h5 className="text-sm font-medium text-gray-700 dark:text-gray-200">Choice {index + 1}</h5>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => handleRemoveChoice(index)}
                className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormGroup label="Value" htmlFor={`config-${configIndex}-choice-${index}-value`} required>
                <TextInput
                  id={`config-${configIndex}-choice-${index}-value`}
                  name={`choice-${index}-value`}
                  value={choice.value}
                  onChange={(e) => handleChoiceChange(index, 'value', e.target.value)}
                  placeholder="Enter choice value"
                  required
                />
              </FormGroup>

              <FormGroup label="Distribution %" htmlFor={`config-${configIndex}-choice-${index}-distribution`} required>
                <TextInput
                  id={`config-${configIndex}-choice-${index}-distribution`}
                  name={`choice-${index}-distribution`}
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={choice.distribution}
                  onChange={(e) => handleChoiceChange(index, 'distribution', Number(e.target.value) || 0)}
                  placeholder="Enter distribution"
                  required
                />
              </FormGroup>
            </div>
          </div>
        ))}

        <Button
          type="button"
          variant="outline"
          onClick={handleAddChoice}
          className="w-full flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Choice
        </Button>

        {choices.length > 0 && (
          <div className={`p-2 rounded text-sm ${
            totalDistribution === 100
              ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
              : 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300'
          }`}>
            Total Distribution: {totalDistribution}%
            {totalDistribution !== 100 && (
              <p className="text-xs mt-1">
                The total distribution should equal 100%. Current difference: {Math.abs(100 - totalDistribution)}%
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
