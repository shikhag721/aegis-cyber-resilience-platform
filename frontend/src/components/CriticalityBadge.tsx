import { Criticality } from "../api/types";

const CLASS_BY_CRITICALITY: Record<Criticality, string> = {
  low: "badge-low",
  medium: "badge-moderate",
  high: "badge-high",
  critical: "badge-critical",
};

export default function CriticalityBadge({ value }: { value: Criticality }) {
  return <span className={`badge ${CLASS_BY_CRITICALITY[value]}`}>{value.toUpperCase()}</span>;
}
