/** Maps a 1-25 likelihood x impact score to the same Low/Moderate/High/
 * Critical bands the backend risk engine will use (Phase 3) - see
 * docs/risk-methodology/README.md once that lands.
 */
function bandFor(score: number): { label: string; className: string } {
  if (score >= 17) return { label: "CRITICAL", className: "badge-critical" };
  if (score >= 10) return { label: "HIGH", className: "badge-high" };
  if (score >= 5) return { label: "MODERATE", className: "badge-moderate" };
  return { label: "LOW", className: "badge-low" };
}

export default function ScoreBadge({ score }: { score: number }) {
  const { label, className } = bandFor(score);
  return (
    <span className={`badge ${className}`}>
      {label} ({score})
    </span>
  );
}
