import { useState, useEffect } from 'react';
import { apiClient } from '../api';
import './ChurnSummary.css';

export default function ChurnSummary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // RE3: useEffect with [] dependency - runs once on component mount
  useEffect(() => {
    const fetchChurnSummary = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getChurnSummary();
        // RE3: Destructuring the response
        const {
          total_customers,
          churned_customers,
          churn_rate,
          by_contract,
        } = response.data;
        setData({
          total_customers,
          churned_customers,
          churn_rate,
          by_contract,
        });
      } catch (err) {
        setError(
          err.response?.data?.detail || 'Failed to fetch churn summary'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchChurnSummary();
  }, []); // RE3: Empty dependency array - fetch only once on mount

  if (loading) {
    return (
      <div className="churn-summary-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading churn analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="churn-summary-container">
        <div className="error-message">
          <span>⚠️ {error}</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  // RE3: API returns churn_rate as percentage already (42.71 not 0.4271)
  const churnPercentage = data.churn_rate.toFixed(1);

  return (
    <div className="churn-summary-container">
      <div className="summary-header">
        <h2>📊 Churn Analytics Dashboard</h2>
        <p>Executive KPIs for customer retention strategy</p>
      </div>

      {/* RE3: Display three metric cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{data.total_customers}</div>
          <div className="metric-label">Total Customers</div>
          <div className="metric-icon">👥</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{data.churned_customers}</div>
          <div className="metric-label">Customers Churned</div>
          <div className="metric-icon">❌</div>
        </div>

        <div className="metric-card churn-rate">
          <div className="metric-value">{churnPercentage}%</div>
          <div className="metric-label">Churn Rate</div>
          <div className="metric-icon">📉</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">
            {data.total_customers - data.churned_customers}
          </div>
          <div className="metric-label">Active Customers</div>
          <div className="metric-icon">✅</div>
        </div>
      </div>

      {/* RE3: Display contract-type churn table */}
      <div className="contract-analysis">
        <h3>📋 Churn Rate by Contract Type</h3>
        <div className="table-container">
          <table className="churn-table">
            <thead>
              <tr>
                <th>Contract Type</th>
                <th>Total</th>
                <th>Churned</th>
                <th>Churn Rate</th>
                <th>Visual</th>
              </tr>
            </thead>
            <tbody>
              {/* RE3: Array rendering with .map() and key prop */}
              {data.by_contract.map((contract) => {
                // RE3: API returns rate as percentage already (42.71, not 0.4271)
                const ratePercentage = contract.churn_rate.toFixed(1);
                // RE3: Proportional bar: width = rate * scale_factor pixels
                const barWidth = contract.churn_rate * 7; // Scale to ~300px max (42.71 * 7 ≈ 300px)

                return (
                  <tr key={contract.contract_type}>
                    <td className="contract-name">{contract.contract_type}</td>
                    <td>{contract.total}</td>
                    <td>{contract.churned}</td>
                    <td className="churn-rate-cell">{ratePercentage}%</td>
                    <td>
                      <div className="bar-container">
                        <div
                          className="churn-bar"
                          style={{ width: `${barWidth}px` }}
                          title={`${ratePercentage}% churn rate`}
                        ></div>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* RE3: Key insights section */}
      <div className="insights-section">
        <h3>💡 Key Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <span className="insight-icon">🎯</span>
            <p>
              Focus retention efforts on{' '}
              <strong>
                {data.by_contract
                  .reduce((max, c) =>
                    c.churn_rate > max.churn_rate ? c : max
                  )
                  .contract_type.toLowerCase()}
              </strong>{' '}
              contracts (highest churn)
            </p>
          </div>
          <div className="insight-card">
            <span className="insight-icon">📈</span>
            <p>
              {data.churned_customers} customers have already churned this
              period
            </p>
          </div>
          <div className="insight-card">
            <span className="insight-icon">🛡️</span>
            <p>Proactive outreach can improve retention rates by 15-20%</p>
          </div>
        </div>
      </div>
    </div>
  );
}
