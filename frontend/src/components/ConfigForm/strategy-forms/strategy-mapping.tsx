import { SeriesForm } from './SeriesForm';
import { RandomNameForm } from './RandomNameForm';
import { ConcatForm } from './ConcatForm';
import { PatternForm } from './PatternForm';
import { DistributedChoiceForm } from './DistributedChoiceForm';
import { DateGeneratorForm } from './DateGeneratorForm';
import { DistributedNumberRangeForm } from './DistributedNumberRangeForm';
import { RandomNumberRangeForm } from './RandomNumberRangeForm';
import { TimeRangeForm } from './TimeRangeForm';
import { ReplacementForm } from './ReplacementForm';
import { DeleteForm } from './DeleteForm';
import { DistributedTimeRangeForm } from './DistributedTimeRangeForm';
import { DistributedDateRangeForm } from './DistributedDateRangeForm';

export const STRATEGY_DESCRIPTIONS = {
  SERIES_STRATEGY: 'Generate sequential numbers with a specified start and step',
  RANDOM_NAME_STRATEGY: 'Generate random names (first, last, or full names)',
  CONCAT_STRATEGY: 'Concatenate values from other columns with optional separator and suffix',
  PATTERN_STRATEGY: 'Generate values matching a specified regex pattern',
  DISTRIBUTED_CHOICE_STRATEGY: 'Choose values from a list with specified distribution percentages',
  DATE_GENERATOR_STRATEGY: 'Generate dates within a specified range',
  DISTRIBUTED_NUMBER_RANGE_STRATEGY: 'Generate numbers within ranges with specified distribution percentages',
  RANDOM_NUMBER_RANGE_STRATEGY: 'Generate random numbers within a specified range',
  TIME_RANGE_STRATEGY: 'Generate times within a specified range',
  DISTRIBUTED_TIME_RANGE_STRATEGY: 'Generate times within multiple ranges with specified distribution percentages',
  DISTRIBUTED_DATE_RANGE_STRATEGY: 'Generate dates within multiple ranges with specified distribution percentages',
  REPLACEMENT_STRATEGY: 'Replace values based on specified rules',
  DELETE_STRATEGY: 'Delete or nullify values based on conditions',
};

export const STRATEGY_FORM_MAPPING = {
  SERIES_STRATEGY: SeriesForm,
  RANDOM_NAME_STRATEGY: RandomNameForm,
  CONCAT_STRATEGY: ConcatForm,
  PATTERN_STRATEGY: PatternForm,
  DISTRIBUTED_CHOICE_STRATEGY: DistributedChoiceForm,
  DATE_GENERATOR_STRATEGY: DateGeneratorForm,
  DISTRIBUTED_NUMBER_RANGE_STRATEGY: DistributedNumberRangeForm,
  RANDOM_NUMBER_RANGE_STRATEGY: RandomNumberRangeForm,
  TIME_RANGE_STRATEGY: TimeRangeForm,
  DISTRIBUTED_TIME_RANGE_STRATEGY: DistributedTimeRangeForm,
  DISTRIBUTED_DATE_RANGE_STRATEGY: DistributedDateRangeForm,
  REPLACEMENT_STRATEGY: ReplacementForm,
  DELETE_STRATEGY: DeleteForm,
} as const;

export type StrategyName = keyof typeof STRATEGY_FORM_MAPPING;
