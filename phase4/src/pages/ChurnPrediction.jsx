import { useState } from 'react';
import { apiClient } from '../api';
import './ChurnPrediction.css';

export default function ChurnPrediction() {
  // RE5: Controlled form inputs
  const [formData, setFormData] = useState({
    customer_id: '',
    tenure: '',
    monthly_charges: '',
    contract_type: 'Month-to-month',
    service_count: '',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const updated = { ...prev };
        delete updated[name];
        return updated;
      });
    }
  };

  // RE5: Form validation
  const validateForm = () => {
    const errors = {};

    if (!formData.tenure || formData.tenure < 0 || formData.tenure > 100) {
      errors.tenure = 'Tenure must be between 0 and 100 months';
    }

    if (
      !formData.monthly_charges ||
      formData.monthly_charges <= 0
    ) {
      errors.monthly_charges =
        'Monthly charges must be greater than 0';
    }

    if (!formData.contract_type) {
      errors.contract_type = 'Contract type is required';
    }

    if (
      !formData.service_count ||
      formData.service_count < 0 ||
      formData.service_count > 6
    ) {
      errors.service_count = 'Service count must be between 0 and 6';
    }

    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      setError('Please fix the validation errors above');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // RE5: POST with JSON body
      const response = await apiClient.predictChurn({
        customer_id: formData.customer_id || null,
        tenure: parseInt(formData.tenure),
        monthly_charges: parseFloat(formData.monthly_charges),
        contract_type: formData.contract_type,
        service_count: parseInt(formData.service_count),
      });

      setResult(response.data);
    } catch (err) {
      // RE5: Handle 422 validation errors from Pydantic
      if (err.response?.status === 422) {
        const detail = err.response.data?.detail;
        if (Array.isArray(detail)) {
          const fieldErrors = {};
          detail.forEach((err) => {
            const field = err.loc?.[1] || 'form';
            fieldErrors[field] = err.msg;
          });
          setValidationErrors(fieldErrors);
          setError('Please fix the validation errors above');
        } else {
          setError(detail || 'Validation error');
        }
      } else {
        setError(
          err.response?.data?.detail ||
            'Failed to make prediction. Make sure the API is running.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // RE5: Determine risk level color coding
  const getRiskLevel = (score) => {
    if (score < 0.3) return { level: 'Low', color: 'green', emoji: '✅' };
    if (score < 0.6) return { level: 'Medium', color: 'amber', emoji: '⚠️' };
    return { level: 'High', color: 'red', emoji: '❌' };
  };

  const riskInfo = result ? getRiskLevel(result.risk_score) : null;

  return (
    <div className="prediction-container">
      <div className="prediction-header">
        <h2>🎯 Churn Prediction</h2>
        <p>
          Enter customer details for instant churn risk assessment using our ML
          model
        </p>
      </div>

      <div className="prediction-content">
        {/* Left side: Form */}
        <div className="form-section">
          <form onSubmit={handleSubmit} className="prediction-form">
            {/* Optional: Customer ID for reference */}
            <div className="form-group">
              <label htmlFor="customer_id">Customer ID (Optional)</label>
              <input
                type="text"
                id="customer_id"
                name="customer_id"
                value={formData.customer_id}
                onChange={handleInputChange}
                placeholder="e.g., 0280-XJGEX"
                className="form-input"
              />
            </div>

            {/* RE5: Controlled input - tenure */}
            <div className="form-group">
              <label htmlFor="tenure">
                Tenure (months) <span className="required">*</span>
              </label>
              <input
                type="number"
                id="tenure"
                name="tenure"
                value={formData.tenure}
                onChange={handleInputChange}
                min="0"
                max="100"
                placeholder="0-100"
                className={`form-input ${
                  validationErrors.tenure ? 'error' : ''
                }`}
              />
              {validationErrors.tenure && (
                <span className="error-text">
                  {validationErrors.tenure}
                </span>
              )}
            </div>

            {/* RE5: Controlled input - monthly_charges */}
            <div className="form-group">
              <label htmlFor="monthly_charges">
                Monthly Charges ($) <span className="required">*</span>
              </label>
              <input
                type="number"
                id="monthly_charges"
                name="monthly_charges"
                value={formData.monthly_charges}
                onChange={handleInputChange}
                min="0"
                step="0.01"
                placeholder="0.00"
                className={`form-input ${
                  validationErrors.monthly_charges ? 'error' : ''
                }`}
              />
              {validationErrors.monthly_charges && (
                <span className="error-text">
                  {validationErrors.monthly_charges}
                </span>
              )}
            </div>

            {/* RE5: Controlled select element */}
            <div className="form-group">
              <label htmlFor="contract_type">
                Contract Type <span className="required">*</span>
              </label>
              <select
                id="contract_type"
                name="contract_type"
                value={formData.contract_type}
                onChange={handleInputChange}
                className={`form-select ${
                  validationErrors.contract_type ? 'error' : ''
                }`}
              >
                <option value="Month-to-month">Month-to-month</option>
                <option value="One year">One year</option>
                <option value="Two year">Two year</option>
              </select>
              {validationErrors.contract_type && (
                <span className="error-text">
                  {validationErrors.contract_type}
                </span>
              )}
            </div>

            {/* RE5: Controlled input - service_count */}
            <div className="form-group">
              <label htmlFor="service_count">
                Services Subscribed <span className="required">*</span>
              </label>
              <input
                type="number"
                id="service_count"
                name="service_count"
                value={formData.service_count}
                onChange={handleInputChange}
                min="0"
                max="6"
                placeholder="0-6"
                className={`form-input ${
                  validationErrors.service_count ? 'error' : ''
                }`}
              />
              {validationErrors.service_count && (
                <span className="error-text">
                  {validationErrors.service_count}
                </span>
              )}
            </div>

            {/* General error message */}
            {error && !Object.keys(validationErrors).length && (
              <div className="error-alert">⚠️ {error}</div>
            )}

            {/* RE5: Loading state on submit button */}
            <button
              type="submit"
              disabled={loading}
              className="submit-button"
            >
              {loading ? '🔄 Predicting...' : '📊 Predict Churn Risk'}
            </button>
          </form>

          <div className="form-info">
            <h4>ℹ️ How It Works</h4>
            <ul>
              <li>Fill in all customer details</li>
              <li>Our ML model analyzes churn risk factors</li>
              <li>Receive instant risk score and recommendation</li>
              <li>Green = Low risk | Amber = Medium | Red = High</li>
            </ul>
          </div>
        </div>

        {/* Right side: Result */}
        <div className="result-section">
          {/* RE5: Show loading state */}
          {loading && (
            <div className="result-placeholder">
              <div className="spinner"></div>
              <p>Analyzing churn risk...</p>
            </div>
          )}

          {/* RE5: Display result with color indicator */}
          {result && !loading && (
            <div className={`risk-card risk-${riskInfo.color}`}>
              <div className="risk-icon">{riskInfo.emoji}</div>
              <div className="risk-title">
                <strong>{riskInfo.level} Risk</strong>
              </div>

              <div className="risk-score">
                <div className="score-value">
                  {(result.risk_score * 100).toFixed(1)}%
                </div>
                <div className="score-label">Churn Probability</div>
              </div>

              <div className="risk-meter">
                <div className="meter-background">
                  <div
                    className={`meter-fill meter-${riskInfo.color}`}
                    style={{
                      width: `${result.risk_score * 100}%`,
                    }}
                  ></div>
                </div>
              </div>

              <div className="prediction-detail">
                <div className="detail-row">
                  <span className="detail-label">Prediction:</span>
                  <span className="detail-value">{result.prediction}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Customer ID:</span>
                  <span className="detail-value">
                    {result.customer_id || 'N/A'}
                  </span>
                </div>
              </div>

              <div className="risk-recommendation">
                {riskInfo.color === 'green' && (
                  <p>
                    ✅ This customer is stable. Maintain regular engagement and
                    monitor for changes.
                  </p>
                )}
                {riskInfo.color === 'amber' && (
                  <p>
                    ⚠️ Medium risk detected. Consider targeted retention offers
                    or improved service quality.
                  </p>
                )}
                {riskInfo.color === 'red' && (
                  <p>
                    🚨 High churn risk. Immediate intervention recommended:
                    special offers, account review, or customer success contact.
                  </p>
                )}
              </div>

              {result.note && (
                <div className="prediction-note">
                  <small>📝 {result.note}</small>
                </div>
              )}

              <button
                onClick={() => {
                  setResult(null);
                  setFormData({
                    customer_id: '',
                    tenure: '',
                    monthly_charges: '',
                    contract_type: 'Month-to-month',
                    service_count: '',
                  });
                }}
                className="reset-button"
              >
                🔄 New Prediction
              </button>
            </div>
          )}

          {!result && !loading && (
            <div className="result-placeholder">
              <div className="placeholder-icon">📊</div>
              <p>Fill in the form and submit to see risk assessment</p>
            </div>
          )}
        </div>
      </div>

      {/* Notes section */}
      <div className="notes-section">
        <h3>📌 Integration Notes</h3>
        <ul>
          <li>
            <strong>RE5:</strong> This demonstrates the complete full-stack
            integration
          </li>
          <li>
            <strong>ML4 Stub:</strong> Currently returns stub predictions
          </li>
          <li>
            <strong>ML5:</strong> After ML4, stub will be replaced with real
            model predictions
          </li>
          <li>
            <strong>API:</strong> Predictions via POST /predict-churn endpoint
          </li>
        </ul>
      </div>
    </div>
  );
}
