const CLASS_BY_BAND: Record<string, string> = {
  low: "badge-low",
  medium: "badge-moderate",
  high: "badge-high",
  critical: "badge-critical",
};

export default function SeverityBadge({ band }: { band: string }) {
  return <span className={`badge ${CLASS_BY_BAND[band] ?? "badge-moderate"}`}>{band.toUpperCase()}</span>;
}
