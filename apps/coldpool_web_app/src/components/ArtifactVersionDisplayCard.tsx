import type { ArtifactVersionView } from "../types/artifactVersion";

type ArtifactVersionDisplayCardProps = {
  artifactVersion: ArtifactVersionView;
};

function formatDateTime(value: string | null): string {
  if (value === null) {
    return "—";
  }

  const parsedDate = new Date(value);
  if (Number.isNaN(parsedDate.getTime())) {
    return value;
  }

  return parsedDate.toLocaleString();
}

function formatBytes(sizeBytes: number): string {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`;
  }

  const units = ["KB", "MB", "GB", "TB"];
  let size = sizeBytes;
  let unitIndex = -1;

  do {
    size /= 1024;
    unitIndex += 1;
  } while (size >= 1024 && unitIndex < units.length - 1);

  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[unitIndex]}`;
}

export default function ArtifactVersionDisplayCard({
  artifactVersion,
}: ArtifactVersionDisplayCardProps) {
  return (
    <article className="artifact-version-card">
      <div className="artifact-version-card__header">
        <div>
          <h2 className="artifact-version-card__title">
            {artifactVersion.artifact_name}
          </h2>
          <p className="artifact-version-card__subtitle">
            Version {artifactVersion.version_label ?? "—"}
          </p>
        </div>
        <span className="artifact-version-card__badge">
          {formatBytes(artifactVersion.size_bytes)}
        </span>
      </div>

      <dl className="artifact-version-card__details">
        <div>
          <dt>Artifact ID</dt>
          <dd>{artifactVersion.artifact_id}</dd>
        </div>
        <div>
          <dt>Version ID</dt>
          <dd>{artifactVersion.version_id}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{formatDateTime(artifactVersion.created_at)}</dd>
        </div>
        <div>
          <dt>Expires</dt>
          <dd>{formatDateTime(artifactVersion.expires_at)}</dd>
        </div>
        <div className="artifact-version-card__full-width">
          <dt>Checksum</dt>
          <dd>{artifactVersion.checksum ?? "—"}</dd>
        </div>
      </dl>
    </article>
  );
}
