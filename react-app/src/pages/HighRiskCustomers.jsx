import { useState, useEffect } from "react";
import api from "../api";

function HighRiskCustomers() {
  const [customers, setCustomers] = useState([]);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);

    // NOTE: the backend currently ignores query params entirely
    // (tracked gap), so changing `limit` will not change the result
    // set yet. Sending it anyway so this page works correctly the
    // moment that gap is fixed, without needing frontend changes.
    api
      .get("/customers/high-risk", { params: { limit } })
      .then((res) => setCustomers(res.data))
      .catch(() => setError("Could not load high-risk customers."))
      .finally(() => setLoading(false));
  }, [limit]);

  const handleSort = () => {
    setCustomers([...customers].sort((a, b) => {
      // Sorting by monthly_charges instead of tenure, since tenure
      // is not currently part of this endpoint's response.
      return sortAsc
        ? a.monthly_charges - b.monthly_charges
        : b.monthly_charges - a.monthly_charges;
    }));
    setSortAsc(!sortAsc);
  };

  return (
    <div>
      <div className="card">
        <h2>High-Risk Customers</h2>
        <p className="muted">
          {loading
            ? "Loading..."
            : `${customers.length} high-risk customers identified`}
        </p>
      </div>

      {error && <p className="error-text">{error}</p>}

      {!loading && !error && customers.length === 0 && (
        <p className="muted">No high-risk customers found.</p>
      )}

      {!loading && customers.length > 0 && (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Gender</th>
                <th>Contract Type</th>
                <th onClick={handleSort}>
                  Monthly Charges {sortAsc ? "▲" : "▼"}
                </th>
                <th>Internet Service</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => (
                <tr key={c.customer_id}>
                  <td>{c.customer_id}</td>
                  <td>{c.gender}</td>
                  <td>{c.contract_type}</td>
                  <td>${Number(c.monthly_charges).toFixed(2)}</td>
                  <td>{c.internet_service}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: 12 }}>
            <button className="primary" onClick={() => setLimit(limit + 50)}>
              Load More
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default HighRiskCustomers;