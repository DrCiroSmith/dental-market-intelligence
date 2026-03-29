import { useState } from 'react';
import './index.css';

interface ValuationResult {
  currentValue: number;
  dsoExit: number;
  arbitrage: number;
}

function App() {
  const [zipCode, setZipCode] = useState("33178");
  const [revenue, setRevenue] = useState(2000000);
  const [ebitda, setEbitda] = useState(525000);
  const [practiceType, setPracticeType] = useState("solo_gp");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValuationResult | null>(null);

  const calculateValuation = async () => {
    setLoading(true);
    try {
      const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${API_BASE}/api/v1/valuate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          net_income: ebitda,
          interest: 0,
          taxes: 0,
          depreciation: 0,
          add_backs: 0,
          practice_type: practiceType
        })
      });

      if (res.ok) {
        const data = await res.json();
        const typicalValue = data.valuation_range.typical_value;
        const exitPot = ebitda * 12.0;

        setResult({
          currentValue: typicalValue,
          dsoExit: exitPot,
          arbitrage: exitPot - typicalValue
        });
      }
    } catch (e) {
      console.error("Backend offline. Fallback mode.");
      // Fallback if APIs are offline during MVP presentation
      const tv = ebitda * (practiceType === 'solo_gp' ? 3.5 : 5.0);
      const ex = ebitda * 12.0;
      setResult({ currentValue: tv, dsoExit: ex, arbitrage: ex - tv });
    }
    setLoading(false);
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
  };

  return (
    <div>
      <div className="title-bar">
        <h1>🦷 ROI Intel Pro v2.1</h1>
      </div>

      <div className="app-container">
        <aside className="sidebar">
          <h3>Market Parameters</h3>

          <div className="input-block">
            <label>📍 Target ZIP Code</label>
            <input value={zipCode} onChange={e => setZipCode(e.target.value)} />
          </div>

          <div className="input-block">
            <label>Annual Revenue ($)</label>
            <input type="number" value={revenue} onChange={e => setRevenue(Number(e.target.value))} />
          </div>

          <div className="input-block">
            <label>Current EBITDA ($)</label>
            <input type="number" value={ebitda} onChange={e => setEbitda(Number(e.target.value))} />
          </div>

          <div className="input-block">
            <label>Market Category</label>
            <select value={practiceType} onChange={e => setPracticeType(e.target.value)}>
              <option value="solo_gp">Solo GP</option>
              <option value="small_group">Small Group (2-5)</option>
              <option value="specialty">Specialty Practice</option>
            </select>
          </div>

          <button className="btn" onClick={calculateValuation}>
            {loading ? "Analyzing..." : "Calculate Arbitrage"}
          </button>
        </aside>

        <main className="main-content">
          <div className="grid">
            <div className="card">
              <div className="card-title">Typical Private Value</div>
              <div className="card-value">{result ? formatCurrency(result.currentValue) : "$0"}</div>
            </div>
            <div className="card">
              <div className="card-title">DSO Exit Potential</div>
              <div className="card-value accent">{result ? formatCurrency(result.dsoExit) : "$0"}</div>
            </div>
            <div className="card" style={{ borderColor: 'var(--primary)' }}>
              <div className="card-title" style={{ color: 'var(--primary)' }}>Arbitrage Gap</div>
              <div className="card-value">{result ? formatCurrency(result.arbitrage) : "$0"}</div>
            </div>
          </div>

          <div className="card" style={{ flex: 1 }}>
            <div className="card-title">Regional NPI Providers Pipeline (Mocked API)</div>
            <table className="providers-table">
              <thead>
                <tr>
                  <th>Provider Name</th>
                  <th>Credential</th>
                  <th>Distance</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Dr. Samantha Lee</td><td>DDS</td><td>1.2 miles</td></tr>
                <tr><td>Dr. Robert Martinez</td><td>DMD</td><td>2.4 miles</td></tr>
                <tr><td>Elite Smiles PLLC</td><td>Clinic</td><td>3.1 miles</td></tr>
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
