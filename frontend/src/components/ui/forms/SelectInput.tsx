import React from 'react';

interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface SelectInputProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  name: string;
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: SelectOption[];
  placeholder?: string; // Text for the first, disabled option
  label?: string; // Optional: if not provided, FormGroup can handle it
  error?: string | null;
  className?: string;
}

const SelectInput: React.FC<SelectInputProps> = ({
  name,
  value,
  onChange,
  options,
  placeholder,
  className = ''
  // label, error, and other HTML select attributes are handled by spread
  , ...props
}) => {
  const baseStyles =
    'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white dark:bg-gray-800 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-gray-900 dark:text-gray-100';
  const errorStyles = 'border-red-500 text-red-900 placeholder-red-700 focus:ring-red-500 focus:border-red-500 dark:text-red-400 dark:border-red-400';
  const disabledStyles = 'bg-gray-100 cursor-not-allowed dark:bg-gray-700 dark:text-gray-400';

  const hasError = 'error' in props && !!props.error;

  return (
    <select
      id={name}
      name={name}
      value={value}
      onChange={onChange}
      className={`${baseStyles} ${hasError ? errorStyles : ''} ${props.disabled ? disabledStyles : ''} ${className}`.trim()}
      {...props}
    >
      {placeholder && (
        <option value="" disabled hidden className="text-gray-500 dark:text-gray-400">
          {placeholder}
        </option>
      )}
      {options.map((option) => (
        <option
          key={option.value}
          value={option.value}
          disabled={option.disabled}
          className="text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800"
        >
          {option.label}
        </option>
      ))}
    </select>
  );
};

export default SelectInput;
