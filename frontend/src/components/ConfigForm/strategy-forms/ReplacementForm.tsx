import React from 'react';
import { Replace } from 'lucide-react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';
import { Button } from '@/components/ui/button';
import { Plus, Trash2 } from 'lucide-react';

interface ReplacementRule {
  pattern: string;
  replacement: string;
  case_sensitive: boolean;
}

interface ReplacementFormProps {
  columnId: string;
  currentParams: Record<string, any>;
  onParamsChange: (columnId: string, paramName: string, value: any) => void;
}

export const ReplacementForm: React.FC<ReplacementFormProps> = ({
  columnId,
  currentParams,
  onParamsChange,
}) => {
  const rules: ReplacementRule[] = currentParams.rules || [];

  const handleAddRule = () => {
    const newRules = [...rules, { pattern: '', replacement: '', case_sensitive: false }];
    onParamsChange(columnId, 'rules', newRules);
  };

  const handleRemoveRule = (index: number) => {
    const newRules = rules.filter((_, i) => i !== index);
    onParamsChange(columnId, 'rules', newRules);
  };

  const handleRuleChange = (index: number, field: keyof ReplacementRule, value: string | boolean) => {
    const newRules = rules.map((rule, i) => {
      if (i === index) {
        return { ...rule, [field]: value };
      }
      return rule;
    });
    onParamsChange(columnId, 'rules', newRules);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h5 className="text-sm font-medium text-gray-700">Replacement Rules</h5>
        <Button
          type="button"
          onClick={handleAddRule}
          variant="outline"
          size="sm"
          className="flex items-center gap-1"
        >
          <Plus className="w-4 h-4" />
          Add Rule
        </Button>
      </div>

      {rules.map((rule, index) => (
        <div key={index} className="p-4 border border-gray-200 rounded-md space-y-3">
          <div className="flex justify-between items-center">
            <h6 className="text-sm font-medium text-gray-600">Rule {index + 1}</h6>
            <Button
              type="button"
              onClick={() => handleRemoveRule(index)}
              variant="ghost"
              size="sm"
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>

          <FormGroup label="Pattern (Regex)" htmlFor={`${columnId}-rule-${index}-pattern`} required>
            <TextInput
              id={`${columnId}-rule-${index}-pattern`}
              name={`rule-${index}-pattern`}
              value={rule.pattern}
              onChange={(e) => handleRuleChange(index, 'pattern', e.target.value)}
              placeholder="e.g., [A-Z]+"
              required
            />
          </FormGroup>

          <FormGroup label="Replacement" htmlFor={`${columnId}-rule-${index}-replacement`} required>
            <TextInput
              id={`${columnId}-rule-${index}-replacement`}
              name={`rule-${index}-replacement`}
              value={rule.replacement}
              onChange={(e) => handleRuleChange(index, 'replacement', e.target.value)}
              placeholder="e.g., X"
              required
            />
          </FormGroup>

          <FormGroup label="Case Sensitive" htmlFor={`${columnId}-rule-${index}-case_sensitive`}>
            <SelectInput
              id={`${columnId}-rule-${index}-case_sensitive`}
              name={`rule-${index}-case_sensitive`}
              value={rule.case_sensitive ? 'true' : 'false'}
              onChange={(e) => handleRuleChange(index, 'case_sensitive', e.target.value === 'true')}
              options={[
                { value: 'true', label: 'Yes' },
                { value: 'false', label: 'No' },
              ]}
            />
          </FormGroup>
        </div>
      ))}

      {rules.length === 0 && (
        <p className="text-sm text-gray-500 text-center py-4">
          Add rules to specify replacements
        </p>
      )}

      <div className="p-3 bg-gray-50 rounded-md">
        <p className="text-sm text-gray-600">
          Rules are applied in order. Each rule can use regex patterns for matching.
        </p>
      </div>
    </div>
  );
}; 