export default function Legend() {
  const levels = [
    { level: "Critical", color: "#dc2626", range: "75–100" },
    { level: "High",     color: "#ea580c", range: "55–74" },
    { level: "Moderate", color: "#ca8a04", range: "35–54" },
    { level: "Low",      color: "#16a34a", range: "0–34" },
  ];

  return (
    <div className="legend">
      <div className="legend-title">RISK INDEX</div>
      {levels.map((l) => (
        <div key={l.level} className="legend-row">
          <span className="legend-swatch" style={{ background: l.color }} />
          <span className="legend-level">{l.level}</span>
          <span className="legend-range">{l.range}</span>
        </div>
      ))}
      <div className="legend-note">Click district for details</div>
    </div>
  );
}
