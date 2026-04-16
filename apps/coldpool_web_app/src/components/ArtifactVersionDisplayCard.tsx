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
    <article
      className="artifact-version-card"
      data-testid={`artifact-version-card-${artifactVersion.version_id}`}
    >
      <div className="artifact-version-card__header">
        <div>
          <h2
            className="artifact-version-card__title"
            data-testid={`artifact-version-card-title-${artifactVersion.version_id}`}
          >
            {artifactVersion.artifact_name}
          </h2>
          <p
            className="artifact-version-card__subtitle"
            data-testid={`artifact-version-card-version-label-${artifactVersion.version_id}`}
          >
            Version {artifactVersion.version_label ?? "—"}
          </p>
        </div>
        <span
          className="artifact-version-card__badge"
          data-testid={`artifact-version-card-size-${artifactVersion.version_id}`}
        >
          {formatBytes(artifactVersion.size_bytes)}
        </span>
      </div>

      <dl className="artifact-version-card__details">
        <div>
          <dt>Artifact ID</dt>
          <dd
            data-testid={`artifact-version-card-artifact-id-${artifactVersion.version_id}`}
          >
            {artifactVersion.artifact_id}
          </dd>
        </div>
        <div>
          <dt>Version ID</dt>
          <dd
            data-testid={`artifact-version-card-version-id-${artifactVersion.version_id}`}
          >
            {artifactVersion.version_id}
          </dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd
            data-testid={`artifact-version-card-created-at-${artifactVersion.version_id}`}
          >
            {formatDateTime(artifactVersion.created_at)}
          </dd>
        </div>
        <div>
          <dt>Expires</dt>
          <dd
            data-testid={`artifact-version-card-expires-at-${artifactVersion.version_id}`}
          >
            {formatDateTime(artifactVersion.expires_at)}
          </dd>
        </div>
        <div className="artifact-version-card__full-width">
          <dt>Checksum</dt>
          <dd
            data-testid={`artifact-version-card-checksum-${artifactVersion.version_id}`}
          >
            {artifactVersion.checksum ?? "—"}
          </dd>
        </div>
      </dl>
    </article>
  );
}
