# Phase 4: React API Consumer - Customer Retention Dashboard

## Overview

This is a complete React application demonstrating how a frontend UI consumes a backend REST API. The application implements the full **RE1-RE5** lab curriculum, showing real-world patterns for API integration, state management, error handling, and form processing.

**Goal**: Students understand how a UI talks to a backend through HTTP requests, handling loading states, errors, and real-time data updates.

---

## Lab Structure (RE1-RE5)

### **RE1: Setup & API Configuration** ✅
- **File**: `src/api.js`
- **Concepts**:
  - Creating axios instance with base URL
  - Environment variables with `REACT_APP_` prefix
  - Centralized API client for all requests
  - Testing API connection on app load
  
**What you'll see**:
- API status indicator in header (connected/connecting/offline)
- Console logs showing API connection test
- Warning banner if API is unreachable

---

### **RE2: Customer Search Page** ✅
- **File**: `src/pages/CustomerSearch.jsx`
- **Endpoint**: `GET /customers/{id}/profile`
- **Concepts**:
  - Controlled input components (`useState` for input value)
  - Click-triggered async fetch (not `useEffect`)
  - 404 error handling ("Customer not found")
  - Conditional rendering with null guards (`customer && <div>...`)
  - Data display in organized card layout
  - Colour-coded churn status (red/green)

**What you'll see**:
- Input field for customer ID (e.g., "0280-XJGEX")
- Search button triggers API call
- Loading spinner while fetching
- Customer profile card with demographics, services, billing
- Error message for unknown customers
- Red/green status indicator

---

### **RE3: Churn Summary Dashboard** ✅
- **File**: `src/pages/ChurnSummary.jsx`
- **Endpoint**: `GET /churn/summary`
- **Concepts**:
  - `useEffect` with empty dependency array `[]` (fetch on mount)
  - Destructuring response data
  - Percentage formatting: `(rate * 100).toFixed(1) + "%"`
  - Array rendering with `.map()` and `key` prop
  - Proportional bar chart: `width = rate * 100 * scale_factor`
  - Loading/error/data state pattern

**What you'll see**:
- 4 metric cards: total customers, churned, churn rate, active
- Contract-type table with churn rates by contract type
- Visual proportional bars showing relative churn rates
- Key insights section with recommendations
- Clean, professional metric display

---

### **RE4: High-Risk Customers Page** ✅
- **File**: `src/pages/HighRiskCustomers.jsx`
- **Endpoint**: `GET /customers/high-risk`
- **Concepts**:
  - `useEffect` with dependency array `[limit, sortAsc, sortColumn]`
  - Re-fetching when dependencies change
  - Sorting without mutating: `[...array].sort()`
  - Toggle state for ascending/descending sort
  - Currency formatting: `"$" + value.toFixed(2)`
  - Empty state handling ("No high-risk customers found")
  - Pagination with "Load More" button
  - List rendering with proper keys

**What you'll see**:
- Table with customer ID, tenure, charges, contract type, status
- Click column headers to sort ascending/descending
- Count badge showing number of high-risk customers
- "Load More" button to fetch next 50 customers
- Colour-coded status badges (at-risk/churned)
- Empty state message if no customers found

---

### **RE5: Churn Prediction** ✅
- **File**: `src/pages/ChurnPrediction.jsx`
- **Endpoint**: `POST /predict-churn`
- **Concepts**:
  - Complex form with 4 controlled inputs (`useState`)
  - Form validation with error messages
  - `POST` with JSON body: `axios.post(url, data)`
  - Handling 422 validation errors from Pydantic
  - `try/catch/finally`: loading state always clears in finally
  - Loading state on submit button
  - Conditional styling: three-level colour coding (green/amber/red)
  - Full-stack integration demo

**What you'll see**:
- Form with: tenure, monthly charges, contract type, service count
- Validation feedback below each field
- Submit button shows "Predicting..." while loading
- Risk card with:
  - Risk level (Low/Medium/High) with emoji
  - Risk score as percentage
  - Probability meter (green/amber/red)
  - Recommendations based on risk level
  - "New Prediction" button to reset form

---

## Quick Start

### Prerequisites
- **Node.js** 16+ and **npm**
- **FastAPI** running on `http://localhost:8000` with CORS enabled

### Installation

1. **Navigate to phase4 directory**:
   ```bash
   cd d:\Training\Project\phase4
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Verify .env file**:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```
   (Already created during setup)

4. **Start development server**:
   ```bash
   npm run dev
   ```
   - Open browser to `http://localhost:3000`
   - Hot-reload enabled: changes save automatically

---

## API Connection Checklist

### ✅ FastAPI must be running

```bash
cd d:\Training\Project
uvicorn main:app --reload
```

**Required endpoints**:
- ✅ `GET /churn/summary` - Churn metrics
- ✅ `GET /customers/{id}/profile` - Customer details
- ✅ `GET /customers/high-risk` - At-risk customers list
- ✅ `POST /predict-churn` - Churn prediction

### ✅ CORS must be enabled in FastAPI

Check `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Project Structure

```
phase4/
├── src/
│   ├── api.js                    # API client configuration (RE1)
│   ├── App.jsx                   # Main app & navigation
│   ├── App.css                   # Global styles
│   ├── index.css                 # Reset & base styles
│   ├── main.jsx                  # Entry point
│   └── pages/
│       ├── CustomerSearch.jsx    # RE2: Customer search
│       ├── CustomerSearch.css
│       ├── ChurnSummary.jsx      # RE3: Dashboard KPIs
│       ├── ChurnSummary.css
│       ├── HighRiskCustomers.jsx # RE4: Risk list
│       ├── HighRiskCustomers.css
│       ├── ChurnPrediction.jsx   # RE5: Prediction form
│       └── ChurnPrediction.css
├── .env                          # Environment variables
├── package.json                  # Dependencies
├── vite.config.js               # Vite bundler config
└── README.md                     # This file
```

---

## Key Concepts Implemented

### **Axios & HTTP Requests**
```javascript
// Get request
const response = await apiClient.getChurnSummary();

// Post request with JSON body
const result = await apiClient.predictChurn({
  tenure: 24,
  monthly_charges: 65.99,
  contract_type: "Month-to-month",
  service_count: 3
});

// Error handling
try {
  await fetch...
} catch (error) {
  if (error.response?.status === 404) {
    // Handle 404
  } else if (error.response?.status === 422) {
    // Handle validation error
  }
}
```

### **React Hooks**
```javascript
// State management
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

// Fetch on mount (empty dependency array)
useEffect(() => {
  fetchData();
}, []); // Runs ONCE when component mounts

// Fetch when dependencies change
useEffect(() => {
  fetchData(limit, sortBy);
}, [limit, sortBy]); // Runs when limit or sortBy change
```

### **Error Handling Patterns**
```javascript
// Graceful degradation
if (error) return <div>{error}</div>;

// 404 Specific handling
if (err.response?.status === 404) {
  setError("Customer not found");
}

// Validation errors from backend
if (err.response?.status === 422) {
  const detail = err.response.data.detail;
  // Parse and display validation errors
}
```

### **Conditional Rendering**
```javascript
// Null guard
{customer && <div>{customer.name}</div>}

// Ternary operator
<span className={customer.churn ? 'churned' : 'active'}>
  {customer.churn ? 'CHURNED' : 'ACTIVE'}
</span>

// Loading state
{loading ? <Spinner /> : <Content />}
```

---

## Testing the APIs

### Test Customer Search (RE2)
Try customer ID: `0280-XJGEX` (should exist in database)

### Test Churn Summary (RE3)
Click "Dashboard" tab - should load on mount

### Test High-Risk Customers (RE4)
Click "High Risk" tab - should show list, click headers to sort

### Test Prediction (RE5)
Enter:
- Tenure: 24
- Monthly Charges: 65.99
- Contract: Month-to-month
- Services: 3

Click "Predict Churn Risk" - should show risk card

---

## Troubleshooting

### "API Offline" warning banner?
- ✅ FastAPI running on `http://localhost:8000`?
- ✅ CORS middleware enabled?
- ✅ Check browser console for error details

### Page shows "Loading..." forever?
- ✅ Check Network tab in browser DevTools (F12)
- ✅ Check FastAPI console for errors
- ✅ API endpoint exists and returns data?

### "Customer not found" (RE2)?
- ✅ Customer ID format correct? (uppercase letters/numbers)
- ✅ Customer exists in database?
- ✅ FastAPI `/customers/{id}/profile` endpoint working?

### Form validation errors (RE5)?
- ✅ All fields filled?
- ✅ Tenure between 0-100?
- ✅ Monthly charges > 0?
- ✅ Service count between 0-6?

---

## Browser DevTools Console

Open DevTools (F12) to see:
```javascript
// RE1: API connection test
🔗 Testing API connection to http://localhost:8000...
✅ API connection successful

// RE2: Fetch logs
GET /customers/0280-XJGEX/profile → 200 OK

// RE3: Dashboard data
{total_customers: 7043, churned: 1869, churn_rate: 0.265}

// Errors
❌ API connection failed: Network Error
```

---

## Learning Outcomes

After completing this lab, students understand:

✅ How React components consume REST APIs  
✅ CORS and why browsers block cross-origin requests  
✅ axios vs fetch: error handling, JSON parsing, interceptors  
✅ useEffect dependency arrays and fetch lifecycle  
✅ Controlled components and form validation  
✅ Loading, error, and success state patterns  
✅ Handling 404, 422, and other HTTP errors  
✅ POST requests with JSON body and validation  
✅ Sorting and pagination from API responses  
✅ Conditional rendering and styling  

---

## Next Steps

- **Phase 5 (DE)**: Data engineering pipeline adds real data
- **Phase 6 (ML)**: ML model predictions replace stub response
- **Full Stack Integration**: RE5 prediction form shows real ML scores

---

## Useful Commands

```bash
# Development
npm run dev              # Start dev server (port 3000)
npm run build            # Production build
npm run preview          # Preview production build

# Linting
npm run lint             # Run ESLint

# Python backend
cd ..
uvicorn main:app --reload  # FastAPI on port 8000
```

---

**Phase 4 Complete**: React app fully consuming FastAPI backend! 🎉
