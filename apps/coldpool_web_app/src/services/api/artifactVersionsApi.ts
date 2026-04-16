import type {
  ArtifactOption,
  ArtifactVersionView,
  CreateArtifactVersionRequest,
} from "../../types/artifactVersion";

const API_BASE_URL = "/api";

async function parseJsonResponse<T>(response: Response): Promise<T> {
  const responseBody = (await response.json()) as T | { error?: string };

  if (!response.ok) {
    const errorMessage =
      typeof responseBody === "object" &&
      responseBody !== null &&
      "error" in responseBody &&
      typeof responseBody.error === "string"
        ? responseBody.error
        : "Request failed.";
    throw new Error(errorMessage);
  }

  return responseBody as T;
}

export async function getAllArtifacts(): Promise<ArtifactOption[]> {
  const response = await fetch(`${API_BASE_URL}/artifacts`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  return parseJsonResponse<ArtifactOption[]>(response);
}

export async function getAllArtifactVersions(): Promise<ArtifactVersionView[]> {
  const response = await fetch(`${API_BASE_URL}/artifact-versions`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  return parseJsonResponse<ArtifactVersionView[]>(response);
}

export async function createArtifactVersion(
  payload: CreateArtifactVersionRequest,
): Promise<ArtifactVersionView> {
  const response = await fetch(`${API_BASE_URL}/artifact-versions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJsonResponse<ArtifactVersionView>(response);
}
