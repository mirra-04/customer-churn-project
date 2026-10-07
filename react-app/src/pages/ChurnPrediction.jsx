import { useState } from "react";
import api from "../api";

const initialForm = {
  tenure: "",
  monthly_charges: "",
  contract_type: "Month-to-month",
  service_count: "",
};

function ChurnPrediction() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.post("/predict-churn", {
        tenure: Number(form.tenure),
        monthly_charges: Number(form.monthly_charges),
        contract_type: form.contract_type,
        service_count: Number(form.service_count),
      });
      setResult(res.data);
    } catch (err) {
      if (err.response?.status === 422) {
        const detail = err.response.data?.detail;
        setError(
          Array.isArray(detail)
            ? detail.map((d) => d.msg).join(", ")
            : detail || "Validation error."
        );
      } else if (err.response?.status === 401) {
        setError("Unauthorized -- check the API key configuration.");
      } else {
        setError("Prediction request failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  // risk_score is a 0-1 fraction from the backend.
  const getRiskLevel = (fraction) => {
    if (fraction < 0.3) return "low";
    if (fraction < 0.6) return "medium";
    return "high";
  };

  return (
    <div>
      <div className="card">
        <h2>Churn Prediction</h2>
        <p className="muted">Enter customer details to get a churn risk score.</p>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12, marginTop: 12 }}>
          <label>
            Tenure (months)
            <input
              type="number"
              min="0"
              required
              value={form.tenure}
              onChange={handleChange("tenure")}
              style={{ width: "100%" }}
            />
          </label>

          <label>
            Monthly Charges ($)
            <input
              type="number"
              min="0"
              step="0.01"
              required
              value={form.monthly_charges}
              onChange={handleChange("monthly_charges")}
              style={{ width: "100%" }}
            />
          </label>

          <label>
            Contract Type
            <select
              value={form.contract_type}
              onChange={handleChange("contract_type")}
              style={{ width: "100%" }}
            >
              <option>Month-to-month</option>
              <option>One year</option>
              <option>Two year</option>
            </select>
          </label>

          <label>
            Number of Services (0-6)
            <input
              type="number"
              min="0"
              max="6"
              required
              value={form.service_count}
              onChange={handleChange("service_count")}
              style={{ width: "100%" }}
            />
          </label>

          <button className="primary" type="submit" disabled={loading}>
            {loading ? "Predicting..." : "Predict Churn Risk"}
          </button>
        </form>
      </div>

      {error && <p className="error-text">{error}</p>}

      {result && (
        <div className="card">
          {(() => {
            const level = getRiskLevel(result.risk_score);
            return (
              <>
                <h3>
                  Risk Score: {(result.risk_score * 100).toFixed(1)}%{" "}
                  <span className={`badge ${level}`}>{level.toUpperCase()}</span>
                </h3>
                <p>{result.prediction}</p>
                {result.confidence != null && (
                  <p className="muted">
                    Confidence: {(result.confidence * 100).toFixed(1)}%
                  </p>
                )}
                {result.note && <p className="muted">{result.note}</p>}
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}

export default ChurnPrediction;
