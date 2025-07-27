import React from 'react';
import type { StrategyCollection, StrategySchema } from '../../types/strategy';
import { STRATEGY_FORM_MAPPING } from './strategy-forms/strategy-mapping';

interface StrategyParametersProps {
  configIndex: number;
  selectedStrategyName: string | undefined;
  strategySchemas: StrategyCollection | undefined;
  currentParams: Record<string, any>;
  onParamsChange: (configIndex: number, paramName: string, value: any) => void;
  availableColumns: string[]; // Required prop for ConcatForm
}

export const StrategyParameters: React.FC<StrategyParametersProps> = ({
  configIndex,
  selectedStrategyName,
  strategySchemas,
  currentParams,
  onParamsChange,
  availableColumns,
}) => {
  if (!selectedStrategyName || !strategySchemas) {
    return <p className="text-sm text-gray-500">Select a strategy to see its parameters.</p>;
  }

  const strategySchema: StrategySchema | undefined = strategySchemas[selectedStrategyName];

  if (!strategySchema) {
    return <p className="text-sm text-red-500">Error: Could not find schema for strategy '{selectedStrategyName}'.</p>;
  }

  // Check if there's a specialized form component for this strategy
  const SpecializedForm = STRATEGY_FORM_MAPPING[selectedStrategyName as keyof typeof STRATEGY_FORM_MAPPING];

  if (SpecializedForm) {
    return (
      <div className="space-y-4 mt-4 pt-4 border-t border-gray-200">
        <h4 className="text-md font-semibold text-gray-700">Strategy Parameters: {strategySchema.strategy_name}</h4>
        <SpecializedForm
          configIndex={configIndex}
          currentParams={currentParams}
          onParamsChange={onParamsChange}
          {...(selectedStrategyName === 'CONCAT_STRATEGY' ? { availableColumns } : {})}
        />
      </div>
    );
  }

  // If no specialized form exists, show a message
  return (
    <div className="space-y-4 mt-4 pt-4 border-t border-gray-200">
      <h4 className="text-md font-semibold text-gray-700">Strategy Parameters: {strategySchema.strategy_name}</h4>
      <p className="text-sm text-gray-500">This strategy has no configurable parameters.</p>
    </div>
  );
};
