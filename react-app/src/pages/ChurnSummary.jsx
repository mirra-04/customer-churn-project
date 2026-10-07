import { useState, useEffect } from "react";
import api from "../api";

function ChurnSummary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/churn/summary")
      .then((res) => setData(res.data))
      .catch(() => setError("Could not load churn summary."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading...</p>;
  if (error) return <p className="error-text">{error}</p>;
  if (!data) return null;

  const { total_customers, churned_customers, churn_rate, by_contract } = data;

  // NOTE: churn_rate and each row's churn_rate here are already on a
  // 0-100 scale (the backend does round(x * 100, 2)), not 0-1 as the
  // original brief assumed. So we display the value directly rather
  // than multiplying by 100 again.
  const maxRate = Math.max(...by_contract.map((c) => c.churn_rate), 1);

  return (
    <div>
      <div className="card">
        <h2>Churn Summary</h2>
        <p className="muted">Key retention metrics across the customer base.</p>
      </div>

      <div className="metric-row">
        <div className="metric-card">
          <div className="metric-value">{total_customers}</div>
          <div className="metric-label">Total Customers</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{churned_customers}</div>
          <div className="metric-label">Churned</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{churn_rate.toFixed(1)}%</div>
          <div className="metric-label">Churn Rate</div>
        </div>
      </div>

      <div className="card">
        <h3>Churn Rate by Contract Type</h3>
        <table>
          <thead>
            <tr>
              <th>Contract Type</th>
              <th>Total</th>
              <th>Churn Rate</th>
            </tr>
          </thead>
          <tbody>
            {by_contract.map((row) => (
              <tr key={row.contract_type}>
                <td>{row.contract_type}</td>
                <td>{row.total}</td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div className="bar-track" style={{ width: 100 }}>
                      <div
                        className="bar-fill"
                        style={{ width: `${(row.churn_rate / maxRate) * 100}%` }}
                      />
                    </div>
                    <span>{row.churn_rate.toFixed(1)}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ChurnSummary;