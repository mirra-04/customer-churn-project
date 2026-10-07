import { useState, useEffect } from 'react';
import { apiClient, BASE_URL } from './api';
import CustomerSearch from './pages/CustomerSearch';
import ChurnSummary from './pages/ChurnSummary';
import HighRiskCustomers from './pages/HighRiskCustomers';
import ChurnPrediction from './pages/ChurnPrediction';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [apiStatus, setApiStatus] = useState('connecting');
  const [apiError, setApiError] = useState(null);

  // RE1: useEffect that calls GET /churn/summary on load
  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log(`🔗 Testing API connection to ${BASE_URL}...`);
        await apiClient.testConnection();
        console.log('✅ API connection successful');
        setApiStatus('connected');
      } catch (error) {
        console.error('❌ API connection failed:', error);
        setApiStatus('failed');
        setApiError(error.message);
      }
    };

    testConnection();
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'search':
        return <CustomerSearch />;
      case 'dashboard':
        return <ChurnSummary />;
      case 'risk':
        return <HighRiskCustomers />;
      case 'prediction':
        return <ChurnPrediction />;
      default:
        return <ChurnSummary />;
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo">📊</div>
            <div>
              <h1>Customer Retention Dashboard</h1>
              <p>Phase 4: React API Consumer - Full-Stack Integration</p>
            </div>
          </div>

          {/* API Status Indicator */}
          <div
            className={`api-status ${apiStatus}`}
            title={
              apiStatus === 'failed' ? apiError : `Connected to ${BASE_URL}`
            }
          >
            <span className={`status-dot ${apiStatus}`}></span>
            <span className="status-text">
              {apiStatus === 'connected'
                ? '✅ API Connected'
                : apiStatus === 'connecting'
                  ? '🔄 Connecting...'
                  : '❌ API Offline'}
            </span>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="app-nav">
        <div className="nav-container">
          <button
            className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentPage('dashboard')}
            title="RE3: Executive KPIs dashboard"
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Dashboard</span>
          </button>

          <button
            className={`nav-item ${currentPage === 'search' ? 'active' : ''}`}
            onClick={() => setCurrentPage('search')}
            title="RE2: Customer profile search"
          >
            <span className="nav-icon">🔍</span>
            <span className="nav-label">Search</span>
          </button>

          <button
            className={`nav-item ${currentPage === 'risk' ? 'active' : ''}`}
            onClick={() => setCurrentPage('risk')}
            title="RE4: High-risk customer list"
          >
            <span className="nav-icon">🚨</span>
            <span className="nav-label">High Risk</span>
          </button>

          <button
            className={`nav-item ${currentPage === 'prediction' ? 'active' : ''}`}
            onClick={() => setCurrentPage('prediction')}
            title="RE5: Churn risk prediction"
          >
            <span className="nav-icon">🎯</span>
            <span className="nav-label">Predict</span>
          </button>
        </div>
      </nav>

      {/* API Connection Warning */}
      {apiStatus === 'failed' && (
        <div className="warning-banner">
          <div className="warning-content">
            <span className="warning-icon">⚠️</span>
            <div>
              <strong>API Connection Failed</strong>
              <p>
                Make sure FastAPI is running on {BASE_URL}. You can start it
                with: <code>uvicorn main:app --reload</code>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="app-main">{renderPage()}</main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>📚 React Labs (RE1-RE5)</h4>
            <ul>
              <li>
                <strong>RE1:</strong> Setup & API configuration
              </li>
              <li>
                <strong>RE2:</strong> Customer search page
              </li>
              <li>
                <strong>RE3:</strong> Churn summary dashboard
              </li>
              <li>
                <strong>RE4:</strong> High-risk customers list
              </li>
              <li>
                <strong>RE5:</strong> Churn prediction form (full-stack)
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>🔌 API Endpoints</h4>
            <ul>
              <li>GET /churn/summary</li>
              <li>GET /customers/&#123;id&#125;/profile</li>
              <li>GET /customers/high-risk</li>
              <li>POST /predict-churn</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>🎯 Key Concepts</h4>
            <ul>
              <li>CORS middleware for cross-origin requests</li>
              <li>Environment variables with REACT_APP_ prefix</li>
              <li>Axios for HTTP requests</li>
              <li>useEffect for data fetching</li>
              <li>Controlled components & form validation</li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>
            Phase 4: React API Consumer | Demonstrating how a UI talks to a
            backend REST API
          </p>
          <p>
            API Base URL: <code>{BASE_URL}</code>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
