import React, { type ReactNode } from 'react';

interface FormGroupProps {
  label: string;
  htmlFor?: string;
  error?: string | null;
  children: ReactNode;
  className?: string;
  required?: boolean;
}

const FormGroup: React.FC<FormGroupProps> = ({ label, htmlFor, error, children, className, required }) => {
  return (
    <div className={`mb-4 ${className || ''}`}>
      <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
};

export default FormGroup;
