import React, { useState, useEffect, type ChangeEvent } from 'react';
import { getStrategySchemas } from '@/lib/api';
import type { StrategyCollection } from '../../types/strategy';
import ColumnConfigItem from './ColumnConfigItem';
// @ts-ignore
import { saveAs } from 'file-saver';
// @ts-ignore
import YAML from 'js-yaml';
import FormGroup from '@/components/ui/forms/FormGroup';
import TextInput from '@/components/ui/forms/TextInput';
import SelectInput from '@/components/ui/forms/SelectInput';
import CheckboxInput from '@/components/ui/forms/CheckboxInput';

// Icons (using simple text for unstyled version)
const AddIcon = () => <span className="font-bold text-lg">+</span>;

// Updated FormData interface to match backend format
export interface FormData {
  metadata: {
    name: string;
    description: string;
    version: string;
    author: string;
    github: string;
    email: string;
    license: string;
  };
  column_name: string[];
  num_of_rows: number;
  shuffle: boolean;
  file_writer_type: 'CSV' | 'Feather' | 'Excel' | 'Json' | 'Parquet'; // UI-friendly, backend will map to CSV_WRITER etc.
  configs: Array<{
    names: string[];
    strategy: {
      name: string;
      params: Record<string, any>;
    };
    mask?: string;
  }>;
}

const initialFormData: FormData = {
  metadata: {
    name: '',
    description: '',
    version: '1.0.0',
    author: '',
    github: '',
    email: '',
    license: 'Apache-2.0'
  },
  column_name: ['new_column_1'],
  num_of_rows: 1000,
  shuffle: true,
  file_writer_type: 'CSV',
  configs: [
    {
      names: ['new_column_1'],
      strategy: {
        name: '',
        params: {}
      },
      mask: ''
    }
  ]
};

const fileWriterOptions = [
    { value: 'CSV', label: 'CSV' },
    { value: 'Feather', label: 'Feather' },
    { value: 'Excel', label: 'Excel' },
    { value: 'Json', label: 'Json' },
    { value: 'Parquet', label: 'Parquet' },
];

const ConfigForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [strategySchemas, setStrategySchemas] = useState<StrategyCollection | undefined>(undefined);
  const [isLoadingStrategies, setIsLoadingStrategies] = useState(true);
  const [errorStrategies, setErrorStrategies] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);


  useEffect(() => {
    const fetchStrategies = async () => {
      setIsLoadingStrategies(true);
      setErrorStrategies(null);
      try {
        const response = await getStrategySchemas();
        if (Object.keys(response).length === 0) {
          setErrorStrategies('No strategies available. Please ensure the backend server is running.');
        } else {
          setStrategySchemas(response);
        }
      } catch (err: any) {
        setErrorStrategies(err.message || 'Failed to load strategies. Please ensure the backend server is running at http://localhost:8000');
        console.error('Strategy loading error:', err);
      }
      setIsLoadingStrategies(false);
    };
    fetchStrategies();
  }, []);

  const handleMetadataChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      metadata: {
        ...prev.metadata,
        [name]: value
      }
    }));
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    let processedValue: string | number | boolean = value;
    const targetType = e.target.type;
    if (targetType === 'checkbox') {
      processedValue = (e.target as HTMLInputElement).checked;
    } else if (targetType === 'number') {
      processedValue = value === '' ? 0 : Number(value);
      // Enforce row limits in demo mode
      if (name === 'num_of_rows') {
        processedValue = Math.min(Math.max(processedValue as number, 1), 5000);
      }
    }
    setFormData(prev => ({ ...prev, [name]: processedValue }));
  };

  // Handler for changes within a column (e.g., name, strategy, mask)
  const handleColumnChange = (index: number, field: 'column_name' | 'strategy_name' | 'mask', value: string) => {
    if (field === 'column_name') {
      // Update both column_name array and configs.names
      setFormData(prev => ({
        ...prev,
        column_name: prev.column_name.map((name, i) => i === index ? value : name),
        configs: prev.configs.map((config, i) => 
          i === index ? { ...config, names: [value] } : config
        )
      }));
    } else if (field === 'strategy_name') {
      setFormData(prev => ({
        ...prev,
        configs: prev.configs.map((config, i) => 
          i === index ? { 
            ...config, 
            strategy: { name: value, params: {} } // Reset params when strategy changes
          } : config
        )
      }));
    } else if (field === 'mask') {
      setFormData(prev => ({
        ...prev,
        configs: prev.configs.map((config, i) => 
          i === index ? { ...config, mask: value } : config
        )
      }));
    }
  };

  // Handler for changes to strategy parameters within a column
  const handleStrategyParamsChange = (configIndex: number, paramName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      configs: prev.configs.map((config, i) => {
        if (i === configIndex) {
          return {
            ...config,
            strategy: {
              ...config.strategy,
              params: {
                ...config.strategy.params,
                [paramName]: value
              }
            }
          };
        }
        return config;
      })
    }));
  };

  const handleAddColumn = () => {
    const newColumnName = `new_column_${formData.column_name.length + 1}`;
    setFormData(prev => ({
      ...prev,
      column_name: [...prev.column_name, newColumnName],
      configs: [
        ...prev.configs,
        {
          names: [newColumnName],
          strategy: {
            name: '',
            params: {}
          },
          mask: ''
        }
      ]
    }));
  };

  const handleRemoveColumn = (indexToRemove: number) => {
    if (formData.column_name.length <= 1) return; // Don't remove if only one column
    
    setFormData(prev => ({
      ...prev,
      column_name: prev.column_name.filter((_, i) => i !== indexToRemove),
      configs: prev.configs.filter((_, i) => i !== indexToRemove)
    }));
  };

  const generateBackendConfig = () => {
    // Map UI file writer type to backend format
    const fileWriterMapping: Record<string, string> = {
      'CSV': 'CSV_WRITER',
      'JSON': 'JSON_WRITER',
      'Json': 'JSON_WRITER',
      'Excel': 'EXCEL_WRITER',
      'Parquet': 'PARQUET_WRITER',
      'Feather': 'FEATHER_WRITER'
    };

    const backendWriterType = fileWriterMapping[formData.file_writer_type] || 'CSV_WRITER';
    const outputExtensions: Record<string, string> = {
      'CSV_WRITER': 'csv',
      'JSON_WRITER': 'json',
      'EXCEL_WRITER': 'xlsx',
      'PARQUET_WRITER': 'parquet',
      'FEATHER_WRITER': 'feather'
    };
    
    const ext = outputExtensions[backendWriterType] || 'csv';
    const safeName = formData.metadata.name.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase() || 'data';

    return {
      metadata: formData.metadata,
      column_name: formData.column_name.filter(name => name && name.trim() !== ''),
      num_of_rows: formData.num_of_rows,
      shuffle: formData.shuffle,
      file_writer: [
        {
          type: backendWriterType,
          params: {
            output_path: `output/${safeName}.${ext}`
          }
        }
      ],
      configs: formData.configs
        .filter(config => config.names[0] && config.names[0].trim() !== '' && config.strategy.name)
        .map(config => ({
          names: config.names,
          strategy: config.strategy,
          ...(config.mask && config.mask.trim() !== '' && { mask: config.mask })
        }))
    };
  };

  const handleDownloadJson = () => {
    const backendConfig = generateBackendConfig();
    const jsonData = JSON.stringify(backendConfig, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    saveAs(blob, `${formData.metadata.name || 'config'}.json`);
  };

  const handleDownloadYaml = () => {
    try {
      const backendConfig = generateBackendConfig();
      const yamlData = YAML.dump(backendConfig, {
        indent: 2,
        lineWidth: -1,
        noRefs: true,
        sortKeys: false
      });
      const blob = new Blob([yamlData], { type: 'application/x-yaml' });
      saveAs(blob, `${formData.metadata.name || 'config'}.yaml`);
    } catch (e) {
      console.error("Error converting to YAML:", e);
      alert("Error generating YAML file. Check console for details.");
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    
    try {
      const backendConfig = generateBackendConfig();
      
  
      
      // Call the new generate_and_download endpoint
      const apiUrl = import.meta.env.DEV 
        ? (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')
        : '';
      const response = await fetch(`${apiUrl}/generate_and_download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendConfig),
      });

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error('Rate limit exceeded. Please wait before trying again.');
        }
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to generate data');
      }

      // Handle the file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      // Get filename from response headers or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'generated_data.zip';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      // Create download link and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      link.remove();
      window.URL.revokeObjectURL(url);
      
      alert('Data generated and download started successfully!');
      
    } catch (error) {
      console.error('Error generating data:', error);
      alert(`Error generating data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mx-auto p-4 md:p-6 lg:p-8 bg-white dark:bg-gray-900 shadow-xl rounded-lg space-y-8">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-10 text-center">Data Generator Configuration</h1>
      
      {/* Demo Banner */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <span className="text-blue-500 text-lg">🚀</span>
          </div>
          <div className="ml-3">
            <p className="text-blue-700 dark:text-blue-300 text-sm">
              <strong>Synthetic Data Generator:</strong> Create realistic datasets with 13+ generation strategies. 
              Configure columns, choose formats, and download your data instantly.
            </p>
          </div>
        </div>
      </div>

      {/* Metadata Section */}
      <fieldset className="p-6 border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-800">
        <legend className="text-xl font-semibold text-gray-700 dark:text-gray-200 px-2">Project Metadata</legend>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-1 mt-4">
          <FormGroup label="Project Name" htmlFor="name" required>
            <TextInput name="name" value={formData.metadata.name} onChange={handleMetadataChange} required />
          </FormGroup>
          <FormGroup label="Version" htmlFor="version" required>
            <TextInput name="version" value={formData.metadata.version} onChange={handleMetadataChange} placeholder="e.g., 1.0.0" required />
          </FormGroup>
          <FormGroup label="Description" htmlFor="description" className="md:col-span-2" required>
            <textarea 
                id="description"
                name="description" 
                value={formData.metadata.description} 
                onChange={handleMetadataChange} 
                rows={3}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
            />
          </FormGroup>
          <FormGroup label="Author (Optional)" htmlFor="author">
            <TextInput name="author" value={formData.metadata.author} onChange={handleMetadataChange} />
          </FormGroup>
          <FormGroup label="Email (Optional)" htmlFor="email">
            <TextInput name="email" type="email" value={formData.metadata.email} onChange={handleMetadataChange} />
          </FormGroup>
          <FormGroup label="GitHub URL (Optional)" htmlFor="github" className="md:col-span-2">
            <TextInput name="github" type="url" value={formData.metadata.github} onChange={handleMetadataChange} placeholder="https://github.com/user/project" />
          </FormGroup>
        </div>
      </fieldset>

      {/* General Settings Section */}
      <fieldset className="p-6 border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-800">
        <legend className="text-xl font-semibold text-gray-700 dark:text-gray-200 px-2">General Settings</legend>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-1 mt-4">
          <FormGroup label="Number of Rows" htmlFor="num_of_rows" required>
            <TextInput 
              name="num_of_rows" 
              type="number" 
              value={formData.num_of_rows} 
              onChange={handleInputChange} 
              min="1"
              required 
            />
          </FormGroup>
          <FormGroup label="Shuffle Data" htmlFor="shuffle" className="flex items-center mt-5 md:mt-auto">
            <CheckboxInput name="shuffle" label="Enable shuffling" checked={formData.shuffle} onChange={handleInputChange} />
          </FormGroup>
        </div>
      </fieldset>

      {/* File Writer Section */}
      <fieldset className="p-6 border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-800">
        <legend className="text-xl font-semibold text-gray-700 dark:text-gray-200 px-2">File Writer</legend>
        <div className="mt-4">
          <FormGroup label="Output Format" htmlFor="file_writer_type" required>
            <SelectInput 
                name="file_writer_type" 
                value={formData.file_writer_type} 
                onChange={handleInputChange} 
                options={fileWriterOptions} 
                required
            />
          </FormGroup>
        </div>
      </fieldset>
      
      {/* Columns Configuration Section */}
      <fieldset className="p-6 border border-gray-300 dark:border-gray-700 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-800 space-y-6">
        <legend className="text-xl font-semibold text-gray-700 dark:text-gray-200 px-2">Column Configuration</legend>
        
        {isLoadingStrategies && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-gray-100"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-300">Loading strategies...</span>
          </div>
        )}
        
        {errorStrategies && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p className="text-red-600 dark:text-red-400 text-center">{errorStrategies}</p>
            <p className="text-sm text-red-500 dark:text-red-400 text-center mt-2">
              Please ensure the backend server is running
            </p>
          </div>
        )}
        
        {!isLoadingStrategies && !errorStrategies && (
          <div className="space-y-6">
            {formData.configs.map((config, index) => (
              <ColumnConfigItem
                key={index}
                index={index}
                columnName={formData.column_name[index] || ''}
                config={config}
                strategySchemas={strategySchemas}
                onColumnChange={handleColumnChange}
                onRemove={handleRemoveColumn}
                onStrategyParamsChange={handleStrategyParamsChange}
                isOnlyColumn={formData.configs.length === 1}
                availableColumns={formData.column_name.filter((_, i) => i !== index)}
              />
            ))}
            <div className="flex justify-end mt-6">
              <button
                type="button"
                onClick={handleAddColumn}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex items-center"
              >
                <AddIcon />
                <span className="ml-2">Add Column</span>
              </button>
            </div>
          </div>
        )}
      </fieldset>



      {/* Action Buttons */}
      <div className="mt-10 pt-6 border-t border-gray-200 space-y-4 md:space-y-0 md:flex md:items-center md:justify-end md:space-x-3">
        <button 
            type="button" 
            onClick={handleDownloadJson} 
            className="w-full md:w-auto px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
        >
            Download Config (JSON)
        </button>
        <button 
            type="button" 
            onClick={handleDownloadYaml} 
            className="w-full md:w-auto px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
        >
            Download Config (YAML)
        </button>
        <button 
            type="submit" 
            disabled={isGenerating}
            className={`w-full md:w-auto px-6 py-3 text-base font-medium text-white rounded-md shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
              isGenerating 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-green-600 hover:bg-green-700'
            }`}
        >
            {isGenerating ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating...
              </div>
            ) : (
              'Generate & Download'
            )}
        </button>
      </div>

      {/* Live Config Display (Optional) */}
      <details className="mt-6 p-4 border border-gray-200 rounded-lg bg-gray-50 shadow">
        <summary className="text-lg font-semibold text-gray-700 cursor-pointer hover:text-blue-600">View Live Configuration (Backend Format)</summary>
        <pre className="mt-3 p-3 bg-gray-900 text-white text-sm rounded-md overflow-x-auto max-h-96">
          {JSON.stringify(generateBackendConfig(), null, 2)}
        </pre>
      </details>

    </form>
  );
};

export default ConfigForm;