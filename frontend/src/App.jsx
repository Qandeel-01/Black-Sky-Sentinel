import { useState, useCallback } from "react";
import Map from "./components/Map";
import AHPPanel from "./components/AHPPanel";
import DistrictCard from "./components/DistrictCard";
import RiskSummaryBar from "./components/RiskSummaryBar";
import Legend from "./components/Legend";
import "./App.css";

const API = "/api";

export default function App() {
  const [results, setResults] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dataMeta, setDataMeta] = useState(null);
  const [lastWeights, setLastWeights] = useState(null);

  const handleCalculate = useCallback(async (weights) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ weights }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || `Server error ${res.status}`);
      }
      const data = await res.json();
      setResults(data.districts);
      setDataMeta(data.meta || null);
      setLastWeights(weights);
      setSelected(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleExport = (format = "json") => {
    if (!results) return;
    
    const timestamp = new Date().toISOString().split("T")[0];
    
    if (format === "json") {
      const payload = {
        generated_at: new Date().toISOString(),
        data_refreshed_at: dataMeta?.updated_at,
        weights_used: lastWeights,
        districts: results.map(d => ({
          rank: d.rank,
          id: d.id,
          name: d.name,
          composite_score: d.composite,
          risk_tier: d.tier,
          population_m: d.population_m,
          area_km2: d.area_km2,
          top_drivers: d.top_drivers,
        }))
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `risk-analysis-${timestamp}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === "csv") {
      const headers = ["Rank", "District", "Composite Score", "Risk Tier", "Population (M)", "Area (km²)"];
      const rows = results.map(d => [
        d.rank,
        d.name,
        d.composite.toFixed(2),
        d.tier,
        d.population_m,
        d.area_km2,
      ]);
      const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `risk-analysis-${timestamp}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="app">
      <RiskSummaryBar results={results} dataMeta={dataMeta} />

      <div className="main-layout">
        <aside className="left-panel">
          <AHPPanel onCalculate={handleCalculate} loading={loading} />
          {error && <div className="error-box">⚠ {error}</div>}
        </aside>

        <main className="map-area">
          <Map
            results={results}
            onDistrictClick={setSelected}
            selectedId={selected?.id}
          />
          <Legend />
          {!results && (
            <div className="map-prompt">
              <div className="prompt-box">
                <div className="prompt-icon">🛰</div>
                <p>Set weights and click <strong>CALCULATE RISK</strong> to analyse Southern Punjab</p>
              </div>
            </div>
          )}
        </main>

        <aside className="right-panel">
          {selected ? (
            <DistrictCard district={selected} onClose={() => setSelected(null)} />
          ) : results ? (
            <div className="rankings-panel">
              <div className="panel-header">
                <span className="panel-title">DISTRICT RANKINGS</span>
                <div className="export-buttons">
                  <button className="export-btn" onClick={() => handleExport("json")} title="Export as JSON">
                    📋
                  </button>
                  <button className="export-btn" onClick={() => handleExport("csv")} title="Export as CSV">
                    📊
                  </button>
                </div>
              </div>
              <div className="rankings-list">
                {results.map((d) => (
                  <button
                    key={d.id}
                    className={`ranking-row ${selected?.id === d.id ? "active" : ""}`}
                    onClick={() => setSelected(d)}
                  >
                    <span className="rank-num">#{d.rank}</span>
                    <span className="rank-name">{d.name}</span>
                    <span className="rank-level" style={{ color: d.tier_color }}>{d.tier}</span>
                    <span className="rank-score" style={{ color: d.tier_color }}>
                      {d.composite.toFixed(1)}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="right-empty">
              <span>Results will appear here after calculation</span>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
