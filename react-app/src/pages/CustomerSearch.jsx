import { useState } from "react";
import api from "../api";

function CustomerSearch() {
  const [customerId, setCustomerId] = useState("");
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!customerId.trim()) return;

    setLoading(true);
    setError(null);
    setCustomer(null);

    try {
      // Using /profile since it's the only endpoint that returns
      // contract_type, monthly_charges, internet_service, and churn
      // together. Note: tenure is not currently returned by this
      // endpoint (tracked gap), so it's omitted below.
      const res = await api.get(`/customers/${customerId}/profile`);
      setCustomer(res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError("Customer not found.");
      } else {
        setError("Something went wrong while fetching the customer.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div>
      <div className="card">
        <h2>Customer Search</h2>
        <p className="muted">Look up a customer by their ID.</p>

        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <input
            type="text"
            placeholder="e.g. 7590-VHVEG"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{ flex: 1 }}
          />
          <button className="primary" onClick={handleSearch} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {loading && <p className="muted">Loading...</p>}
      {error && <p className="error-text">{error}</p>}

      {customer && (
        <div className="card">
          <h3>{customer.customer_id}</h3>
          <table>
            <tbody>
              <tr>
                <td>Gender</td>
                <td>{customer.gender}</td>
              </tr>
              <tr>
                <td>Contract Type</td>
                <td>{customer.contract_type}</td>
              </tr>
              <tr>
                <td>Internet Service</td>
                <td>{customer.internet_service}</td>
              </tr>
              <tr>
                <td>Monthly Charges</td>
                <td>${Number(customer.monthly_charges).toFixed(2)}</td>
              </tr>
              <tr>
                <td>Total Charges</td>
                <td>
                  {customer.total_charges != null
                    ? `$${Number(customer.total_charges).toFixed(2)}`
                    : "N/A"}
                </td>
              </tr>
              <tr>
                <td>Churn Status</td>
                <td>
                  <span
                    className={`badge ${customer.churn === 1 ? "churned" : "active"}`}
                  >
                    {customer.churn === 1 ? "Churned" : "Active"}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default CustomerSearch;