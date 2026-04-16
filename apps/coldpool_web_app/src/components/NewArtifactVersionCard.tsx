import { useEffect, useMemo, useState } from "react";

import type {
  ArtifactOption,
  CreateArtifactVersionRequest,
} from "../types/artifactVersion";

type NewArtifactVersionCardProps = {
  artifactOptions: ArtifactOption[];
  isSubmitting: boolean;
  submitError: string | null;
  onSubmit: (payload: CreateArtifactVersionRequest) => Promise<void>;
};

type ArtifactMode = "existing" | "new";

type FormState = {
  artifactMode: ArtifactMode;
  existingArtifactId: string;
  newArtifactName: string;
  newArtifactPriorityScore: string;
  newArtifactDesiredCopyCount: string;
  newArtifactType: string;
  newArtifactShelfLifeDays: string;
  versionLabel: string;
  createdAt: string;
  sizeBytes: string;
  checksum: string;
  expiresAt: string;
};

function getDefaultCreatedAtValue(): string {
  const now = new Date();
  const timezoneOffsetMs = now.getTimezoneOffset() * 60 * 1000;
  const localDate = new Date(now.getTime() - timezoneOffsetMs);
  return localDate.toISOString().slice(0, 16);
}

function buildInitialFormState(
  artifactOptions: ArtifactOption[],
  preferredMode?: ArtifactMode,
): FormState {
  const defaultMode: ArtifactMode =
    preferredMode ?? (artifactOptions.length > 0 ? "existing" : "new");

  return {
    artifactMode: defaultMode,
    existingArtifactId:
      artifactOptions.length > 0 ? String(artifactOptions[0].id) : "",
    newArtifactName: "",
    newArtifactPriorityScore: "100",
    newArtifactDesiredCopyCount: "1",
    newArtifactType: "",
    newArtifactShelfLifeDays: "",
    versionLabel: "",
    createdAt: getDefaultCreatedAtValue(),
    sizeBytes: "",
    checksum: "",
    expiresAt: "",
  };
}

export default function NewArtifactVersionCard({
  artifactOptions,
  isSubmitting,
  submitError,
  onSubmit,
}: NewArtifactVersionCardProps) {
  const computedInitialState = useMemo(
    () => buildInitialFormState(artifactOptions),
    [artifactOptions],
  );

  const [formState, setFormState] = useState<FormState>(computedInitialState);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    setFormState((currentState) => {
      const artifactMode =
        currentState.artifactMode === "existing" && artifactOptions.length === 0
          ? "new"
          : currentState.artifactMode;

      const existingArtifactId = artifactOptions.some(
        (artifactOption) =>
          String(artifactOption.id) === currentState.existingArtifactId,
      )
        ? currentState.existingArtifactId
        : artifactOptions.length > 0
          ? String(artifactOptions[0].id)
          : "";

      return {
        ...currentState,
        artifactMode,
        existingArtifactId,
      };
    });
  }, [artifactOptions]);

  function updateField<Key extends keyof FormState>(
    fieldName: Key,
    value: FormState[Key],
  ): void {
    setFormState((currentState) => ({
      ...currentState,
      [fieldName]: value,
    }));
  }

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();
    setLocalError(null);

    try {
      const parsedSizeBytes = Number.parseInt(formState.sizeBytes, 10);
      if (Number.isNaN(parsedSizeBytes) || parsedSizeBytes < 0) {
        throw new Error("Size bytes must be a non-negative integer.");
      }

      let payload: CreateArtifactVersionRequest;

      if (formState.artifactMode === "existing") {
        const parsedArtifactId = Number.parseInt(
          formState.existingArtifactId,
          10,
        );
        if (Number.isNaN(parsedArtifactId) || parsedArtifactId <= 0) {
          throw new Error("Please select an existing artifact.");
        }

        payload = {
          artifact_id: parsedArtifactId,
          new_artifact: null,
          version_label: formState.versionLabel.trim() || null,
          created_at: new Date(formState.createdAt).toISOString(),
          size_bytes: parsedSizeBytes,
          checksum: formState.checksum.trim() || null,
          expires_at: formState.expiresAt
            ? new Date(formState.expiresAt).toISOString()
            : null,
        };
      } else {
        const parsedPriorityScore = Number.parseInt(
          formState.newArtifactPriorityScore,
          10,
        );
        const parsedDesiredCopyCount = Number.parseInt(
          formState.newArtifactDesiredCopyCount,
          10,
        );
        const parsedShelfLifeDays = formState.newArtifactShelfLifeDays
          ? Number.parseInt(formState.newArtifactShelfLifeDays, 10)
          : null;

        if (!formState.newArtifactName.trim()) {
          throw new Error("New artifact name is required.");
        }
        if (Number.isNaN(parsedPriorityScore) || parsedPriorityScore < 0) {
          throw new Error("Priority score must be a non-negative integer.");
        }
        if (
          Number.isNaN(parsedDesiredCopyCount) ||
          parsedDesiredCopyCount < 0
        ) {
          throw new Error("Desired copy count must be a non-negative integer.");
        }
        if (
          parsedShelfLifeDays !== null &&
          (Number.isNaN(parsedShelfLifeDays) || parsedShelfLifeDays < 0)
        ) {
          throw new Error("Shelf life days must be a non-negative integer.");
        }

        payload = {
          artifact_id: null,
          new_artifact: {
            name: formState.newArtifactName.trim(),
            priority_score: parsedPriorityScore,
            desired_copy_count: parsedDesiredCopyCount,
            artifact_type: formState.newArtifactType.trim() || null,
            shelf_life_days: parsedShelfLifeDays,
          },
          version_label: formState.versionLabel.trim() || null,
          created_at: new Date(formState.createdAt).toISOString(),
          size_bytes: parsedSizeBytes,
          checksum: formState.checksum.trim() || null,
          expires_at: formState.expiresAt
            ? new Date(formState.expiresAt).toISOString()
            : null,
        };
      }

      await onSubmit(payload);
      setFormState(
        buildInitialFormState(artifactOptions, formState.artifactMode),
      );
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : "Submit failed.");
    }
  }

  return (
    <section
      className="new-artifact-version-card"
      data-testid="new-artifact-version-card"
    >
      <div className="new-artifact-version-card__header">
        <h1 data-testid="page-title">Coldpool</h1>
        <p>Create a new artifact version or a brand new artifact.</p>
      </div>

      <form
        className="new-artifact-version-card__form"
        onSubmit={handleSubmit}
        data-testid="new-artifact-version-form"
      >
        <div className="new-artifact-version-card__mode-row">
          <label>
            <input
              data-testid="artifact-mode-existing"
              type="radio"
              name="artifactMode"
              value="existing"
              checked={formState.artifactMode === "existing"}
              onChange={() => updateField("artifactMode", "existing")}
              disabled={artifactOptions.length === 0 || isSubmitting}
            />
            Existing artifact
          </label>
          <label>
            <input
              data-testid="artifact-mode-new"
              type="radio"
              name="artifactMode"
              value="new"
              checked={formState.artifactMode === "new"}
              onChange={() => updateField("artifactMode", "new")}
              disabled={isSubmitting}
            />
            New artifact
          </label>
        </div>

        {formState.artifactMode === "existing" ? (
          <label className="form-field">
            <span>Artifact</span>
            <select
              data-testid="existing-artifact-select"
              value={formState.existingArtifactId}
              onChange={(event) =>
                updateField("existingArtifactId", event.target.value)
              }
              disabled={artifactOptions.length === 0 || isSubmitting}
            >
              {artifactOptions.length === 0 ? (
                <option value="">No artifacts available</option>
              ) : (
                artifactOptions.map((artifactOption) => (
                  <option key={artifactOption.id} value={artifactOption.id}>
                    {artifactOption.name}
                  </option>
                ))
              )}
            </select>
          </label>
        ) : (
          <div className="new-artifact-version-card__grid">
            <label className="form-field">
              <span>Artifact name</span>
              <input
                data-testid="new-artifact-name-input"
                value={formState.newArtifactName}
                onChange={(event) =>
                  updateField("newArtifactName", event.target.value)
                }
                disabled={isSubmitting}
              />
            </label>

            <label className="form-field">
              <span>Priority score</span>
              <input
                data-testid="new-artifact-priority-score-input"
                type="number"
                min="0"
                value={formState.newArtifactPriorityScore}
                onChange={(event) =>
                  updateField("newArtifactPriorityScore", event.target.value)
                }
                disabled={isSubmitting}
              />
            </label>

            <label className="form-field">
              <span>Desired copy count</span>
              <input
                data-testid="new-artifact-desired-copy-count-input"
                type="number"
                min="0"
                value={formState.newArtifactDesiredCopyCount}
                onChange={(event) =>
                  updateField("newArtifactDesiredCopyCount", event.target.value)
                }
                disabled={isSubmitting}
              />
            </label>

            <label className="form-field">
              <span>Artifact type</span>
              <input
                data-testid="new-artifact-type-input"
                value={formState.newArtifactType}
                onChange={(event) =>
                  updateField("newArtifactType", event.target.value)
                }
                disabled={isSubmitting}
              />
            </label>

            <label className="form-field">
              <span>Shelf life days</span>
              <input
                data-testid="new-artifact-shelf-life-days-input"
                type="number"
                min="0"
                value={formState.newArtifactShelfLifeDays}
                onChange={(event) =>
                  updateField("newArtifactShelfLifeDays", event.target.value)
                }
                disabled={isSubmitting}
              />
            </label>
          </div>
        )}

        <div className="new-artifact-version-card__grid">
          <label className="form-field">
            <span>Version label</span>
            <input
              data-testid="version-label-input"
              value={formState.versionLabel}
              onChange={(event) =>
                updateField("versionLabel", event.target.value)
              }
              disabled={isSubmitting}
            />
          </label>

          <label className="form-field">
            <span>Created at</span>
            <input
              data-testid="created-at-input"
              type="datetime-local"
              value={formState.createdAt}
              onChange={(event) => updateField("createdAt", event.target.value)}
              disabled={isSubmitting}
            />
          </label>

          <label className="form-field">
            <span>Size bytes</span>
            <input
              data-testid="size-bytes-input"
              type="number"
              min="0"
              value={formState.sizeBytes}
              onChange={(event) => updateField("sizeBytes", event.target.value)}
              disabled={isSubmitting}
            />
          </label>

          <label className="form-field">
            <span>Checksum</span>
            <input
              data-testid="checksum-input"
              value={formState.checksum}
              onChange={(event) => updateField("checksum", event.target.value)}
              disabled={isSubmitting}
            />
          </label>

          <label className="form-field">
            <span>Expires at</span>
            <input
              data-testid="expires-at-input"
              type="datetime-local"
              value={formState.expiresAt}
              onChange={(event) => updateField("expiresAt", event.target.value)}
              disabled={isSubmitting}
            />
          </label>
        </div>

        {(localError || submitError) && (
          <p
            className="form-error"
            data-testid="new-artifact-version-form-error"
          >
            {localError ?? submitError}
          </p>
        )}

        <div className="new-artifact-version-card__actions">
          <button
            data-testid="create-artifact-version-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Saving..." : "Create artifact version"}
          </button>
        </div>
      </form>
    </section>
  );
}
