import { useEffect, useState } from "react";

import ArtifactVersionDisplayCard from "../components/ArtifactVersionDisplayCard";
import NewArtifactVersionCard from "../components/NewArtifactVersionCard";
import {
  createArtifactVersion,
  getAllArtifactVersions,
  getAllArtifacts,
} from "../services/api/artifactVersionsApi";
import type {
  ArtifactOption,
  ArtifactVersionView,
  CreateArtifactVersionRequest,
} from "../types/artifactVersion";

export default function ArtifactVersionsPage() {
  const [artifactOptions, setArtifactOptions] = useState<ArtifactOption[]>([]);
  const [artifactVersions, setArtifactVersions] = useState<
    ArtifactVersionView[]
  >([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function loadPageData(): Promise<void> {
    setPageError(null);
    setIsLoading(true);

    try {
      const [loadedArtifacts, loadedVersions] = await Promise.all([
        getAllArtifacts(),
        getAllArtifactVersions(),
      ]);

      setArtifactOptions(loadedArtifacts);
      setArtifactVersions(loadedVersions);
    } catch (error) {
      setPageError(
        error instanceof Error ? error.message : "Failed to load data.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadPageData();
  }, []);

  async function handleCreateArtifactVersion(
    payload: CreateArtifactVersionRequest,
  ): Promise<void> {
    setSubmitError(null);
    setIsSubmitting(true);

    try {
      await createArtifactVersion(payload);
      await loadPageData();
    } catch (error) {
      setSubmitError(
        error instanceof Error
          ? error.message
          : "Failed to create artifact version.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="artifact-versions-page">
      <div className="artifact-versions-page__top">
        <NewArtifactVersionCard
          artifactOptions={artifactOptions}
          isSubmitting={isSubmitting}
          submitError={submitError}
          onSubmit={handleCreateArtifactVersion}
        />
      </div>

      <section className="artifact-versions-page__list-section">
        <div className="artifact-versions-page__list-header">
          <h2>Artifact versions</h2>
          <p>{artifactVersions.length} version(s)</p>
        </div>

        {isLoading ? (
          <div className="artifact-versions-page__empty-state">
            Loading artifact versions...
          </div>
        ) : pageError ? (
          <div className="artifact-versions-page__empty-state page-error">
            {pageError}
          </div>
        ) : artifactVersions.length === 0 ? (
          <div className="artifact-versions-page__empty-state">
            No artifact versions found yet.
          </div>
        ) : (
          <div className="artifact-versions-page__list">
            {artifactVersions.map((artifactVersion) => (
              <ArtifactVersionDisplayCard
                key={artifactVersion.version_id}
                artifactVersion={artifactVersion}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
