import { useState, useEffect } from "react";
import api from "./api";
import CustomerSearch from "./pages/CustomerSearch";
import ChurnSummary from "./pages/ChurnSummary";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";
import "./App.css";

const TABS = [
  { id: "summary", label: "Churn Summary", component: ChurnSummary },
  { id: "search", label: "Customer Search", component: CustomerSearch },
  { id: "highrisk", label: "High-Risk Customers", component: HighRiskCustomers },
  { id: "predict", label: "Churn Prediction", component: ChurnPrediction },
];

function App() {
  const [activeTab, setActiveTab] = useState("summary");

  // RE1 — one-time sanity check that the API is reachable and
  // CORS is configured correctly. Runs once on mount ([] dependency).
  useEffect(() => {
    api
      .get("/churn/summary")
      .then((res) => {
        console.log("API connectivity check OK:", res.data);
      })
      .catch((err) => {
        console.error("API connectivity check FAILED:", err);
      });
  }, []);

  const ActiveComponent = TABS.find((t) => t.id === activeTab).component;

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Customer Retention Dashboard</h1>
      </header>

      <nav className="tab-nav">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={activeTab === tab.id ? "tab active" : "tab"}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="tab-content">
        <ActiveComponent />
      </main>
    </div>
  );
}

export default App;