import React, { type ChangeEvent } from 'react';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';
import type { StrategyCollection } from '../../types/strategy';
import { StrategyParameters } from '@/components/ConfigForm/StrategyParameters';

const DeleteIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
    <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.58.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25V4.075c.827-.05 1.66-.075 2.5-.075zM8.086 9.22a.75.75 0 00-1.06 1.06L10 13.34l3.03-3.03a.75.75 0 10-1.06-1.06L10.5 11.72V6.75a.75.75 0 00-1.5 0v4.97l-.914-.914z" clipRule="evenodd" />
    <path d="M3 9.75A.75.75 0 013.75 9h12.5a.75.75 0 010 1.5H3.75A.75.75 0 013 9.75z" />
 </svg>
);

interface ColumnConfigItemProps {
  index: number;
  columnName: string;
  config: {
    names: string[];
    strategy: {
      name: string;
      params: Record<string, any>;
    };
    mask?: string;
  };
  strategySchemas: StrategyCollection | undefined;
  onColumnChange: (index: number, field: 'column_name' | 'strategy_name' | 'mask', value: string) => void;
  onRemove: (index: number) => void;
  onStrategyParamsChange: (configIndex: number, paramName: string, value: any) => void;
  isOnlyColumn: boolean;
  availableColumns: string[];
}

const ColumnConfigItem: React.FC<ColumnConfigItemProps> = ({
  index,
  columnName,
  config,
  strategySchemas,
  onColumnChange,
  onRemove,
  onStrategyParamsChange,
  isOnlyColumn,
  availableColumns,
}) => {
  const handleColumnNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    onColumnChange(index, 'column_name', e.target.value);
  };

  const handleStrategyChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onColumnChange(index, 'strategy_name', e.target.value);
  };

  const handleMaskChange = (e: ChangeEvent<HTMLInputElement>) => {
    onColumnChange(index, 'mask', e.target.value);
  };

  const strategyOptions = strategySchemas
    ? Object.values(strategySchemas).map(s => {

        return {
          value: s.strategy_name,
          label: `${s.strategy_name}${s.description ? ` - ${s.description}` : ''}`,
        };
      })
    : [];



  return (
    <div className="p-4 mb-4 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm bg-gray-50 dark:bg-gray-800 space-y-3">
      <div className="flex justify-between items-center">
        <h4 className="text-md font-semibold text-gray-800 dark:text-gray-200">
          Column: {columnName || '(Untitled)'}
        </h4>
        <button
          type="button"
          onClick={() => onRemove(index)}
          disabled={isOnlyColumn}
          className="p-1 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed rounded hover:bg-red-100 dark:hover:bg-red-900/20"
          aria-label="Remove column"
        >
          <DeleteIcon />
        </button>
      </div>

      <FormGroup label="Column Name" htmlFor={`column-${index}-name`} required>
        <TextInput
          id={`column-${index}-name`}
          name="column_name"
          value={columnName}
          onChange={handleColumnNameChange}
          required
        />
      </FormGroup>

      <FormGroup label="Strategy" htmlFor={`column-${index}-strategy`}>
        <SelectInput
          id={`column-${index}-strategy`}
          name="strategy"
          value={config.strategy.name || ''}
          onChange={handleStrategyChange}
          options={strategyOptions}
          placeholder="Select a strategy"
        />
      </FormGroup>

      {config.strategy.name && strategySchemas && (
        <StrategyParameters
          configIndex={index}
          selectedStrategyName={config.strategy.name}
          strategySchemas={strategySchemas}
          currentParams={config.strategy.params || {}}
          onParamsChange={onStrategyParamsChange}
          availableColumns={availableColumns}
        />
      )}

      <FormGroup label="Mask (Optional)" htmlFor={`column-${index}-mask`}>
        <TextInput
          id={`column-${index}-mask`}
          name="mask"
          value={config.mask || ''}
          onChange={handleMaskChange}
          placeholder="e.g., condition or filter expression"
        />
      </FormGroup>
    </div>
  );
};

export default ColumnConfigItem;
