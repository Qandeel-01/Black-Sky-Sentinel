export default function RiskSummaryBar({ results, dataMeta }) {
  if (!results?.length) return null;

  const counts = { Critical: 0, High: 0, Moderate: 0, Low: 0 };
  results.forEach((d) => counts[d.tier]++);
  const top3 = results.slice(0, 3);

  return (
    <div className="summary-bar" role="region" aria-label="Risk summary dashboard">
      <div className="summary-title-block">
        <div className="summary-title">BLACK SKY — SOUTHERN PUNJAB RISK INDEX</div>
        {dataMeta?.updated_at && (
          <div className="summary-meta" aria-live="polite">
            Updated {new Date(dataMeta.updated_at).toLocaleString()}
          </div>
        )}
      </div>

      <div className="summary-counts" role="group" aria-label="Risk level distribution">
        {Object.entries(counts).map(([level, count]) => (
          <div key={level} className={`summary-chip chip-${level.toLowerCase()}`} title={`${count} district${count !== 1 ? 's' : ''} in ${level} risk`}>
            <span className="chip-count" aria-label={`${count}`}>{count}</span>
            <span className="chip-label">{level}</span>
          </div>
        ))}
      </div>

      <div className="top3" role="group" aria-label="Highest risk districts">
        <span className="top3-label">HIGHEST RISK:</span>
        {top3.map((d, i) => (
          <span key={d.id} className="top3-item" title={`Rank ${i + 1}: ${d.name} - ${d.composite.toFixed(1)} (${d.tier})`}>
            <span className="top3-rank">#{i + 1}</span>
            <span className="top3-name">{d.name}</span>
            <span className="top3-score" style={{ color: d.tier_color }}>
              {d.composite.toFixed(1)}
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}
