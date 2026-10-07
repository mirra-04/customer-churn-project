import { useState } from 'react';
import { apiClient } from '../api';
import './CustomerSearch.css';

export default function CustomerSearch() {
  const [customerId, setCustomerId] = useState('');
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const formatCurrency = (value) => {
    if (value === null || value === undefined || value === '') {
      return 'N/A';
    }

    const numericValue = Number(value);
    if (!Number.isFinite(numericValue)) {
      return 'N/A';
    }

    return `$${numericValue.toFixed(2)}`;
  };

  const handleSearch = async () => {
    if (!customerId.trim()) {
      setError('Please enter a customer ID');
      return;
    }

    setLoading(true);
    setError(null);
    setCustomer(null);

    try {
      const response = await apiClient.getCustomerProfile(customerId);
      setCustomer(response.data);
    } catch (err) {
      // RE2: Handle 404 gracefully - show "Customer not found"
      if (err.response?.status === 404) {
        setError(`Customer "${customerId}" not found`);
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch customer profile');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="customer-search-container">
      <div className="search-header">
        <h2>🔍 Customer Search</h2>
        <p>Enter a customer ID to view their full profile and churn status</p>
      </div>

      {/* RE2: Controlled text input for customer ID */}
      <div className="search-box">
        <input
          type="text"
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter customer ID (e.g., 0280-XJGEX)"
          className="search-input"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="search-button"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* RE2: Show error message for unknown customers */}
      {error && (
        <div className="error-message">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* RE2: Show loading spinner */}
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading customer profile...</p>
        </div>
      )}

      {/* RE2: Display result in a card layout - null guard: customer && ... */}
      {customer && (
        <div className="profile-card">
          <div className="card-header">
            <h3>Customer Profile: {customer.customer_id}</h3>
          </div>

          <div className="card-grid">
            <div className="card-section">
              <h4>Demographics</h4>
              <div className="info-row">
                <span className="label">Gender:</span>
                <span className="value">{customer.gender}</span>
              </div>
              <div className="info-row">
                <span className="label">Senior Citizen:</span>
                <span className="value">{customer.senior_citizen ? 'Yes' : 'No'}</span>
              </div>
              <div className="info-row">
                <span className="label">Partner:</span>
                <span className="value">{customer.partner ? 'Yes' : 'No'}</span>
              </div>
              <div className="info-row">
                <span className="label">Dependents:</span>
                <span className="value">{customer.dependents ? 'Yes' : 'No'}</span>
              </div>
            </div>

            <div className="card-section">
              <h4>Service Details</h4>
              <div className="info-row">
                <span className="label">Tenure:</span>
                <span className="value">{customer.tenure || 'N/A'} months</span>
              </div>
              <div className="info-row">
                <span className="label">Contract Type:</span>
                <span className="value">{customer.contract_type}</span>
              </div>
              <div className="info-row">
                <span className="label">Internet Service:</span>
                <span className="value">{customer.internet_service}</span>
              </div>
              <div className="info-row">
                <span className="label">Payment Method:</span>
                <span className="value">{customer.payment_method}</span>
              </div>
            </div>

            <div className="card-section">
              <h4>Billing</h4>
              <div className="info-row">
                <span className="label">Monthly Charges:</span>
                <span className="value">{formatCurrency(customer.monthly_charges)}</span>
              </div>
              <div className="info-row">
                <span className="label">Total Charges:</span>
                <span className="value">{formatCurrency(customer.total_charges)}</span>
              </div>
            </div>

            {/* RE2: Churn status colour-coded (red/green) */}
            <div className="card-section">
              <h4>Status</h4>
              <div
                className={`churn-status ${
                  customer.churn ? 'churned' : 'active'
                }`}
              >
                {customer.churn ? '❌ CHURNED' : '✅ ACTIVE'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
