'use client';

import { FilterState } from '@/types';

interface FiltersProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  availableProviders: string[];
  availableCountries: string[];
  availablePaymentMethods: string[];
}

export default function Filters({
  filters,
  onChange,
  availableProviders,
  availableCountries,
  availablePaymentMethods,
}: FiltersProps) {
  const handleProviderToggle = (provider: string) => {
    const newProviders = filters.providers.includes(provider)
      ? filters.providers.filter(p => p !== provider)
      : [...filters.providers, provider];
    onChange({ ...filters, providers: newProviders });
  };

  const handleCountryToggle = (country: string) => {
    const newCountries = filters.countries.includes(country)
      ? filters.countries.filter(c => c !== country)
      : [...filters.countries, country];
    onChange({ ...filters, countries: newCountries });
  };

  const handlePaymentMethodToggle = (method: string) => {
    const newMethods = filters.paymentMethods.includes(method)
      ? filters.paymentMethods.filter(m => m !== method)
      : [...filters.paymentMethods, method];
    onChange({ ...filters, paymentMethods: newMethods });
  };

  const handleDateChange = (type: 'start' | 'end', value: string) => {
    const newDateRange = { ...filters.dateRange };
    newDateRange[type] = value ? new Date(value) : null;
    onChange({ ...filters, dateRange: newDateRange });
  };

  const handleClearFilters = () => {
    onChange({
      dateRange: { start: null, end: null },
      providers: [],
      countries: [],
      paymentMethods: [],
    });
  };

  const activeFilterCount =
    filters.providers.length +
    filters.countries.length +
    filters.paymentMethods.length +
    (filters.dateRange.start ? 1 : 0) +
    (filters.dateRange.end ? 1 : 0);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Filters</h2>
        {activeFilterCount > 0 && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear All ({activeFilterCount})
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date Range
          </label>
          <div className="space-y-2">
            <input
              type="date"
              value={filters.dateRange.start?.toISOString().split('T')[0] || ''}
              onChange={(e) => handleDateChange('start', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Start date"
            />
            <input
              type="date"
              value={filters.dateRange.end?.toISOString().split('T')[0] || ''}
              onChange={(e) => handleDateChange('end', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="End date"
            />
          </div>
        </div>

        {/* Providers */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Providers ({filters.providers.length} selected)
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {availableProviders.map(provider => (
              <label key={provider} className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded">
                <input
                  type="checkbox"
                  checked={filters.providers.includes(provider)}
                  onChange={() => handleProviderToggle(provider)}
                  className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">{provider}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Countries */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Countries ({filters.countries.length} selected)
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {availableCountries.map(country => (
              <label key={country} className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded">
                <input
                  type="checkbox"
                  checked={filters.countries.includes(country)}
                  onChange={() => handleCountryToggle(country)}
                  className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">{country}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Payment Methods */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Payment Methods ({filters.paymentMethods.length} selected)
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {availablePaymentMethods.map(method => (
              <label key={method} className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded">
                <input
                  type="checkbox"
                  checked={filters.paymentMethods.includes(method)}
                  onChange={() => handlePaymentMethodToggle(method)}
                  className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700 capitalize">{method.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
