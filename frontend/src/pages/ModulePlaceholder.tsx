interface Props {
  title: string;
  phase: string;
}

/**
 * Placeholder for a module not yet built in the current phase. Kept
 * intentionally explicit (not a fake empty table) so a reviewer looking at
 * the running app can see exactly what's implemented vs. planned - see
 * CHANGELOG.md for phase status.
 */
export default function ModulePlaceholder({ title, phase }: Props) {
  return (
    <div>
      <h1 className="page-title">{title}</h1>
      <p className="page-subtitle">Planned for {phase} - see CHANGELOG.md for current build status.</p>
      <div className="card">
        This module's backend API and UI have not been built yet in this phased build.
        Check the project's GitHub commit history / CHANGELOG.md for progress.
      </div>
    </div>
  );
}
