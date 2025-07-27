import React from 'react';

interface TextInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  name: string;
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  label?: string; // Optional: if not provided, FormGroup can handle it
  error?: string | null;
  type?: 'text' | 'email' | 'password' | 'number' | 'url';
  className?: string;
}

const TextInput: React.FC<TextInputProps> = ({
  name,
  value,
  onChange,
  placeholder,
  type = 'text',
  className = ''
  // label, error, and other HTML input attributes are handled by spread
  , ...props
}) => {
  const baseStyles =
    'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-gray-900 bg-white dark:bg-gray-800 dark:text-gray-100 dark:border-gray-600';
  const errorStyles = 'border-red-500 text-red-900 placeholder-red-700 focus:ring-red-500 focus:border-red-500 dark:text-red-400 dark:border-red-400';
  const disabledStyles = 'bg-gray-100 cursor-not-allowed dark:bg-gray-700 dark:text-gray-400';

  // If an error prop is passed directly (not via FormGroup), apply error styles
  const hasError = 'error' in props && !!props.error;

  return (
    <input
      id={name}
      name={name}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`${baseStyles} ${hasError ? errorStyles : ''} ${props.disabled ? disabledStyles : ''} ${className}`.trim()}
      {...props} // Spread other native input props like disabled, required, min, max, etc.
    />
  );
};

export default TextInput;
