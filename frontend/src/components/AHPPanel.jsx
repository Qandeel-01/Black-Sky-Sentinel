import { useState } from "react";

const CRITERIA = [
  { id: "blackout", label: "Complete Blackout Vulnerability", icon: "⚡", desc: "NEPRA load-shedding severity (hrs/day)" },
  { id: "flood",    label: "Flood Vulnerability",             icon: "🌊", desc: "NDMA monsoon 2022 flood exposure" },
  { id: "heat",     label: "Heat Stress Index",               icon: "🌡️", desc: "Open-Meteo historical max temperatures" },
  { id: "internet", label: "4G Coverage Gap",                icon: "📡", desc: "PTA 4G coverage deficit" },
  { id: "health",   label: "Healthcare Access Deficit",       icon: "🏥", desc: "OSM hospitals & clinics per capita" },
  { id: "infra",    label: "Infrastructure Gap",              icon: "🏗️", desc: "OSM power substations & comm towers" },
  { id: "popexp",   label: "Population Exposure",             icon: "👥", desc: "PBS census × NDMA flood ratio" },
];

const SCENARIOS = [
  {
    id: "default",
    name: "Equal Weight",
    icon: "⚖️",
    desc: "All criteria weighted equally",
    weights: { blackout: 5, flood: 5, heat: 5, internet: 5, health: 5, infra: 5, popexp: 5 },
  },
  {
    id: "flood_season",
    name: "Monsoon Season",
    icon: "🌊",
    desc: "Prioritise flood & population exposure",
    weights: { blackout: 4, flood: 10, heat: 5, internet: 3, health: 6, infra: 4, popexp: 9 },
  },
  {
    id: "grid_crisis",
    name: "Grid Crisis",
    icon: "⚡",
    desc: "Prioritise blackouts & infrastructure",
    weights: { blackout: 10, flood: 3, heat: 4, internet: 3, health: 4, infra: 8, popexp: 5 },
  },
  {
    id: "heat_wave",
    name: "Heat Wave",
    icon: "🌡️",
    desc: "Prioritise heat & healthcare access",
    weights: { blackout: 6, flood: 2, heat: 10, internet: 3, health: 9, infra: 4, popexp: 7 },
  },
  {
    id: "comms_blackout",
    name: "Comms Blackout",
    icon: "📡",
    desc: "Prioritise internet & infrastructure",
    weights: { blackout: 5, flood: 4, heat: 2, internet: 10, health: 4, infra: 8, popexp: 5 },
  },
];

export default function AHPPanel({ onCalculate, loading }) {
  const [weights, setWeights] = useState(
    Object.fromEntries(CRITERIA.map((c) => [c.id, 5]))
  );
  const [hovered, setHovered] = useState(null);
  const [selectedScenario, setSelectedScenario] = useState("default");

  const handleSlider = (id, val) => {
    setWeights((prev) => ({ ...prev, [id]: Number(val) }));
    setSelectedScenario(null); // Deselect scenario when manually adjusting
  };

  const applyScenario = (scenario) => {
    setWeights(scenario.weights);
    setSelectedScenario(scenario.id);
  };

  const resetAll = () => {
    setWeights(Object.fromEntries(CRITERIA.map((c) => [c.id, 5])));
    setSelectedScenario("default");
  };

  const total = Object.values(weights).reduce((a, b) => a + b, 0);

  return (
    <div className="ahp-panel">
      <div className="panel-header">
        <span className="panel-title">AHP WEIGHT MODEL</span>
        <button className="reset-btn" onClick={resetAll} title="Reset to default">RESET</button>
      </div>
      <p className="panel-sub">Adjust criterion importance (1=Low, 10=Critical)</p>

      {/* Scenario Quick Buttons */}
      <div className="scenarios-section">
        <div className="scenarios-label">QUICK SCENARIOS</div>
        <div className="scenarios-grid">
          {SCENARIOS.map((scenario) => (
            <button
              key={scenario.id}
              className={`scenario-btn ${selectedScenario === scenario.id ? "active" : ""}`}
              onClick={() => applyScenario(scenario)}
              title={scenario.desc}
              aria-label={`${scenario.name}: ${scenario.desc}`}
              aria-pressed={selectedScenario === scenario.id}
              disabled={loading}
            >
              <span className="scenario-icon" aria-hidden="true">{scenario.icon}</span>
              <span className="scenario-name">{scenario.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="criteria-list" role="group" aria-label="Risk criteria weights">
        {CRITERIA.map((c) => {
          const pct = total > 0 ? ((weights[c.id] / total) * 100).toFixed(1) : 0;
          return (
            <div
              key={c.id}
              className="criterion-row"
              onMouseEnter={() => setHovered(c.id)}
              onMouseLeave={() => setHovered(null)}
              role="group"
              aria-label={c.label}
            >
              <div className="criterion-top">
                <span className="criterion-icon" aria-hidden="true">{c.icon}</span>
                <span className="criterion-label">{c.label}</span>
                <span className="criterion-pct" aria-live="polite">{pct}%</span>
              </div>
              {hovered === c.id && (
                <p className="criterion-desc">{c.desc}</p>
              )}
              <div className="slider-row">
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={weights[c.id]}
                  onChange={(e) => handleSlider(c.id, e.target.value)}
                  className="slider"
                  style={{ "--val": `${(weights[c.id] - 1) / 9 * 100}%` }}
                  aria-label={`${c.label} weight`}
                  aria-valuenow={weights[c.id]}
                  aria-valuemin="1"
                  aria-valuemax="10"
                />
                <span className="slider-val" aria-hidden="true">{weights[c.id]}</span>
              </div>
              <div className="weight-bar-bg">
                <div className="weight-bar-fill" style={{ width: `${pct}%` }} aria-hidden="true" />
              </div>
            </div>
          );
        })}
      </div>

      <button
        className="calculate-btn"
        onClick={() => onCalculate(weights)}
        disabled={loading}
      >
        {loading ? "CALCULATING…" : "▶  CALCULATE RISK"}
      </button>
    </div>
  );
}
