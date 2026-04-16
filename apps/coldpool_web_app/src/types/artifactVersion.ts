export type ArtifactOption = {
  id: number;
  name: string;
};

export type ArtifactVersionView = {
  version_id: number;
  artifact_id: number;
  artifact_name: string;
  version_label: string | null;
  created_at: string;
  size_bytes: number;
  checksum: string | null;
  expires_at: string | null;
};

export type NewArtifactPayload = {
  name: string;
  priority_score: number;
  desired_copy_count: number;
  artifact_type: string | null;
  shelf_life_days: number | null;
};

export type CreateArtifactVersionRequest = {
  artifact_id: number | null;
  new_artifact: NewArtifactPayload | null;
  version_label: string | null;
  created_at: string;
  size_bytes: number;
  checksum: string | null;
  expires_at: string | null;
};
