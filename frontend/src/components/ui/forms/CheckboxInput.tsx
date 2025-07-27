import React from 'react';

interface CheckboxInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  name: string;
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label: string; // Label is mandatory for checkboxes for accessibility
  error?: string | null;
  className?: string; // For the wrapper div
  inputClassName?: string; // For the input element itself
  labelClassName?: string; // For the label text
}

const CheckboxInput: React.FC<CheckboxInputProps> = ({
  name,
  checked,
  onChange,
  label,
  error,
  className = ''
  , inputClassName = ''
  , labelClassName = ''
  , ...props
}) => {
  const baseInputStyles =
    'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500';
  const errorInputStyles = 'border-red-500 focus:ring-red-500';

  const hasError = !!error;

  return (
    <div className={`flex items-center ${className}`.trim()}>
      <input
        id={name}
        name={name}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className={`${baseInputStyles} ${hasError ? errorInputStyles : ''} ${inputClassName}`.trim()}
        aria-describedby={error ? `${name}-error` : undefined}
        {...props}
      />
      <label htmlFor={name} className={`ml-2 block text-sm text-gray-900 dark:text-gray-100 ${labelClassName}`.trim()}>
        {label}
      </label>
      {/* Error message typically handled by FormGroup, but can be shown here if needed specifically */}
      {/* {error && <p id={`${name}-error`} className="mt-1 text-xs text-red-600">{error}</p>} */}
    </div>
  );
};

export default CheckboxInput;
