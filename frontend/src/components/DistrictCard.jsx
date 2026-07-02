export default function DistrictCard({ district, onClose }) {
  if (!district) return null;

  const color = district.tier_color || "#6b7280";

  return (
    <div className="district-card" role="region" aria-label={`Details for ${district.name}`}>
      <div className="card-header" style={{ borderColor: color }}>
        <div>
          <h2 className="card-name">{district.name}</h2>
          <span className="card-division">Southern Punjab</span>
        </div>
        <div className="card-top-right">
          <span className="risk-badge" style={{ background: color }} role="status">
            {district.tier}
          </span>
          <button className="close-btn" onClick={onClose} aria-label="Close details panel">✕</button>
        </div>
      </div>

      <div className="card-stats-row" role="group" aria-label="District statistics">
        <div className="stat-box">
          <span className="stat-label">Risk Score</span>
          <span className="stat-value" style={{ color }}>{district.composite.toFixed(1)}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Rank</span>
          <span className="stat-value">#{district.rank}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Population</span>
          <span className="stat-value">{district.population_m.toFixed(2)}M</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Area</span>
          <span className="stat-value">{district.area_km2?.toLocaleString()} km²</span>
        </div>
      </div>

      <div className="breakdown-section">
        <h3 className="section-title">Criterion Breakdown</h3>
        <div role="group" aria-label="Risk criteria scores and contributions">
          {Object.entries(district.breakdown).map(([key, val]) => (
            <div key={key} className="breakdown-row">
              <div className="breakdown-top">
                <span className="breakdown-label">{val.label}</span>
                <span className="breakdown-vals">
                  <span className="raw-val" aria-label={`Raw score ${val.score.toFixed(1)}`}>{val.score.toFixed(1)}</span>
                  <span className="weighted-val" aria-label={`Weighted contribution ${val.weighted.toFixed(1)} points`}>→ {val.weighted.toFixed(1)} pts</span>
                </span>
              </div>
              <div className="breakdown-bar-bg" role="progressbar" aria-valuenow={Math.round(val.score)} aria-valuemin="0" aria-valuemax="100">
                <div
                  className="breakdown-bar-fill"
                  style={{ width: `${val.score}%`, background: color }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {district.raw && (
        <div className="meta-section">
          <h3 className="section-title">Raw Indicators</h3>
          <div className="meta-grid">
            <div className="meta-item">
              <span className="meta-key">⚡ Load Shedding</span>
              <span className="meta-val">{district.raw.load_shedding_h} hrs/day</span>
            </div>
            <div className="meta-item">
              <span className="meta-key">🌡 Max Temp</span>
              <span className="meta-val">{district.raw.mean_max_temp_c}°C</span>
            </div>
            <div className="meta-item">
              <span className="meta-key">🏥 Hospitals (OSM)</span>
              <span className="meta-val">{district.raw.hospitals_osm}</span>
            </div>
            <div className="meta-item">
              <span className="meta-key">📡 4G Coverage Gap</span>
              <span className="meta-val">{district.raw.pta_4g_pct}% coverage</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
