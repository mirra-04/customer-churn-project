import { useState, useEffect } from 'react';
import { apiClient } from '../api';
import './HighRiskCustomers.css';

export default function HighRiskCustomers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [limit, setLimit] = useState(50);
  const [sortAsc, setSortAsc] = useState(true);
  const [sortColumn, setSortColumn] = useState('tenure');

  // RE4: useEffect with dependency [limit] - re-fetches when limit state changes
  useEffect(() => {
    const fetchHighRiskCustomers = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getHighRiskCustomers(limit);
        // RE4: Sorting without mutating original array
        let sorted = [...response.data];
        sorted.sort((a, b) => {
          const aVal = a[sortColumn];
          const bVal = b[sortColumn];
          const comparison =
            typeof aVal === 'string'
              ? aVal.localeCompare(bVal)
              : aVal - bVal;
          return sortAsc ? comparison : -comparison;
        });
        setCustomers(sorted);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            'Failed to fetch high-risk customers'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchHighRiskCustomers();
  }, [limit, sortAsc, sortColumn]);

  // RE4: Toggle sort state
  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortAsc(!sortAsc);
    } else {
      setSortColumn(column);
      setSortAsc(true);
    }
  };

  const handleLoadMore = () => {
    setLimit((prev) => prev + 50);
  };

  if (error) {
    return (
      <div className="high-risk-container">
        <div className="error-message">
          <span>⚠️ {error}</span>
        </div>
      </div>
    );
  }

  // RE4: Handle the case where 0 results are returned
  const isEmpty = !loading && customers.length === 0;

  return (
    <div className="high-risk-container">
      <div className="risk-header">
        <h2>🚨 High-Risk Customers</h2>
        <p>Customers flagged for retention outreach priority</p>
      </div>

      {/* RE4: Show a count banner */}
      <div className="risk-summary">
        <div className="count-badge">
          {isEmpty ? (
            <span>✓ No high-risk customers at this time</span>
          ) : (
            <span>
              <strong>{customers.length}</strong> high-risk customers
              identified
            </span>
          )}
        </div>
      </div>

      {isEmpty && !loading && (
        <div className="empty-state">
          <div className="empty-icon">👍</div>
          <h3>No high-risk customers found</h3>
          <p>Excellent! All customers appear to be stable.</p>
        </div>
      )}

      {loading && customers.length === 0 && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading high-risk customers...</p>
        </div>
      )}

      {!isEmpty && (
        <>
          {/* RE4: Interactive table with sorting */}
          <div className="table-container">
            <table className="risk-table">
              <thead>
                <tr>
                  {/* RE4: Sort toggle on tenure column */}
                  <th onClick={() => handleSort('customer_id')}>
                    Customer ID{' '}
                    {sortColumn === 'customer_id' &&
                      (sortAsc ? '↑' : '↓')}
                  </th>
                  <th onClick={() => handleSort('tenure')}>
                    Tenure (months){' '}
                    {sortColumn === 'tenure' && (sortAsc ? '↑' : '↓')}
                  </th>
                  {/* RE4: Format monthly_charges as currency */}
                  <th onClick={() => handleSort('monthly_charges')}>
                    Monthly Charges{' '}
                    {sortColumn === 'monthly_charges' &&
                      (sortAsc ? '↑' : '↓')}
                  </th>
                  <th onClick={() => handleSort('contract_type')}>
                    Contract Type{' '}
                    {sortColumn === 'contract_type' &&
                      (sortAsc ? '↑' : '↓')}
                  </th>
                  <th>Internet Service</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {/* RE4: List rendering with .map(), key={customer.customer_id} */}
                {customers.map((customer) => (
                  <tr key={customer.customer_id} className="risk-row">
                    <td className="customer-id">
                      <code>{customer.customer_id}</code>
                    </td>
                    <td>{customer.tenure || 'N/A'}</td>
                    {/* RE4: Format as currency: "$" + value.toFixed(2) */}
                    <td className="charges">
                      ${customer.monthly_charges.toFixed(2)}
                    </td>
                    <td>
                      <span className="contract-badge">
                        {customer.contract_type}
                      </span>
                    </td>
                    <td>{customer.internet_service}</td>
                    <td>
                      <span
                        className={`status-badge ${
                          customer.churn ? 'churned' : 'at-risk'
                        }`}
                      >
                        {customer.churn ? '❌ CHURNED' : '⚠️ AT-RISK'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* RE4: Load More button */}
          {loading && customers.length > 0 && (
            <div className="loading-more">
              <div className="spinner-small"></div>
              <p>Loading more customers...</p>
            </div>
          )}

          {!loading && customers.length > 0 && customers.length % 50 === 0 && (
            <div className="load-more-section">
              <button
                onClick={handleLoadMore}
                className="load-more-button"
              >
                📥 Load More Customers (Next 50)
              </button>
            </div>
          )}
        </>
      )}

      {/* Info section */}
      <div className="risk-info">
        <h3>ℹ️ About This Page</h3>
        <p>
          This list shows customers flagged by business rules as high-risk for
          churn. After <strong>ML5</strong>, this page displays actual ML model
          scores alongside rule-based flags.
        </p>
      </div>
    </div>
  );
}
