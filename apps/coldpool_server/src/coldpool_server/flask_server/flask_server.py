from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

from coldpool_server.artifact.artifact import Artifact
from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.pool.pool_loader import PoolLoader


class FlaskServer:
    """Minimal Flask server for the first Coldpool web/API version."""

    def __init__(self) -> None:
        """Create the Flask application and register all routes."""
        self.frontend_dist_dir = self._resolve_frontend_dist_dir()
        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self) -> None:
        """Register HTTP routes on the Flask application."""
        self.app.add_url_rule(
            "/api/health",
            view_func=self.get_health,
            methods=["GET"],
        )
        self.app.add_url_rule(
            "/api/artifacts",
            view_func=self.get_all_artifacts,
            methods=["GET"],
        )
        self.app.add_url_rule(
            "/api/artifact-versions",
            view_func=self.get_all_artifact_versions,
            methods=["GET"],
        )
        self.app.add_url_rule(
            "/api/artifact-versions",
            view_func=self.create_new_artifact_version,
            methods=["POST"],
        )
        self.app.add_url_rule(
            "/",
            view_func=self.serve_frontend_index,
            methods=["GET"],
        )
        self.app.add_url_rule(
            "/<path:requested_path>",
            view_func=self.serve_frontend_path,
            methods=["GET"],
        )

    def run(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        debug: bool = False,
    ) -> None:
        """Run the Flask development server."""
        self.app.run(host=host, port=port, debug=debug)

    @staticmethod
    def get_health() -> tuple[Any, int]:
        """Return a minimal health-check response."""
        return jsonify({"status": "ok"}), 200

    @staticmethod
    def get_all_artifacts() -> tuple[Any, int]:
        """Return all artifacts as small objects for UI selection."""
        pool = PoolLoader.get_current_pool()

        artifacts_payload = [
            {
                "id": artifact.id,
                "name": artifact.name,
            }
            for artifact in pool.artifacts
        ]

        return jsonify(artifacts_payload), 200

    @staticmethod
    def get_all_artifact_versions() -> tuple[Any, int]:
        """Return all artifact versions flattened for UI listing."""
        pool = PoolLoader.get_current_pool()

        version_payload: list[dict[str, Any]] = []
        for artifact in pool.artifacts:
            for version in artifact.get_versions():
                version_payload.append(
                    {
                        "version_id": version.id,
                        "artifact_id": artifact.id,
                        "artifact_name": artifact.name,
                        "version_label": version.version_label,
                        "created_at": version.created_at.isoformat(),
                        "size_bytes": version.size_bytes,
                        "checksum": version.checksum,
                        "expires_at": (version.expires_at.isoformat() if version.expires_at is not None else None),
                    }
                )

        version_payload.sort(
            key=lambda item: (
                item["artifact_name"],
                item["created_at"],
                item["version_id"],
            )
        )

        return jsonify(version_payload), 200

    @staticmethod
    def create_new_artifact_version() -> tuple[Any, int]:
        """Create a new version for an existing artifact or a new artifact."""
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        artifact_id = payload.get("artifact_id")
        new_artifact_payload = payload.get("new_artifact")

        if (artifact_id is None and new_artifact_payload is None) or (artifact_id is not None and new_artifact_payload is not None):
            return (
                jsonify({"error": ("Provide exactly one of 'artifact_id' or 'new_artifact'.")}),
                400,
            )

        try:
            pool = PoolLoader.get_current_pool()

            artifact = FlaskServer._resolve_or_create_artifact(
                pool=pool,
                artifact_id=artifact_id,
                new_artifact_payload=new_artifact_payload,
            )

            new_version = ArtifactVersion(
                id=FlaskServer._get_next_version_id(pool),
                artifact=artifact,
                version_label=FlaskServer._optional_str(payload.get("version_label")),
                created_at=FlaskServer._parse_created_at(payload.get("created_at")),
                size_bytes=FlaskServer._required_non_negative_int(
                    payload.get("size_bytes"),
                    field_name="size_bytes",
                ),
                checksum=FlaskServer._optional_str(payload.get("checksum")),
                expires_at=FlaskServer._parse_optional_datetime(payload.get("expires_at")),
                copies=[],
            )

            artifact.add_version(new_version)

            PoolLoader.dump_pool(pool)
            reloaded_pool = PoolLoader.get_current_pool()
            saved_version = reloaded_pool.get_version_by_id(new_version.id)

            if saved_version is None:
                raise ValueError(f"Newly created ArtifactVersion id={new_version.id} was not found after reload.")

            return (
                jsonify(
                    {
                        "version_id": saved_version.id,
                        "artifact_id": saved_version.artifact.id,
                        "artifact_name": saved_version.artifact.name,
                        "version_label": saved_version.version_label,
                        "created_at": saved_version.created_at.isoformat(),
                        "size_bytes": saved_version.size_bytes,
                        "checksum": saved_version.checksum,
                        "expires_at": (saved_version.expires_at.isoformat() if saved_version.expires_at is not None else None),
                    }
                ),
                201,
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    def serve_frontend_index(self) -> Any:
        """Serve the React single-page application entrypoint."""
        return send_from_directory(self.frontend_dist_dir, "index.html")

    def serve_frontend_path(self, requested_path: str) -> Any:
        """Serve frontend static files or fall back to the SPA entrypoint."""
        if requested_path.startswith("api/"):
            return jsonify({"error": "Not found."}), 404

        requested_file = self.frontend_dist_dir / requested_path
        if requested_file.is_file():
            return send_from_directory(self.frontend_dist_dir, requested_path)

        return send_from_directory(self.frontend_dist_dir, "index.html")

    @staticmethod
    def _resolve_or_create_artifact(
        pool: Any,
        artifact_id: Any,
        new_artifact_payload: Any,
    ) -> Artifact:
        """Return an existing artifact or create a new one from payload."""
        if artifact_id is not None:
            if not isinstance(artifact_id, int) or artifact_id <= 0:
                raise ValueError("'artifact_id' must be a positive integer.")

            artifact = pool.get_artifact_by_id(artifact_id)
            if artifact is None:
                raise ValueError(f"Artifact with id={artifact_id} was not found.")
            return artifact

        if not isinstance(new_artifact_payload, dict):
            raise ValueError("'new_artifact' must be a JSON object.")

        artifact_name = FlaskServer._required_non_blank_str(
            new_artifact_payload.get("name"),
            field_name="new_artifact.name",
        )

        if any(existing_artifact.name == artifact_name for existing_artifact in pool.artifacts):
            raise ValueError(f"Artifact with name='{artifact_name}' already exists.")

        artifact = Artifact(
            id=FlaskServer._get_next_artifact_id(pool),
            name=artifact_name,
            priority_score=FlaskServer._required_non_negative_int(
                new_artifact_payload.get("priority_score"),
                field_name="new_artifact.priority_score",
            ),
            desired_copy_count=FlaskServer._required_non_negative_int(
                new_artifact_payload.get("desired_copy_count"),
                field_name="new_artifact.desired_copy_count",
            ),
            artifact_type=FlaskServer._optional_str(new_artifact_payload.get("artifact_type")),
            shelf_life_days=FlaskServer._optional_non_negative_int(
                new_artifact_payload.get("shelf_life_days"),
                field_name="new_artifact.shelf_life_days",
            ),
        )

        pool.artifacts.append(artifact)
        return artifact

    @staticmethod
    def _get_next_artifact_id(pool: Any) -> int:
        """Return the next available artifact id."""
        if not pool.artifacts:
            return 1
        return max(artifact.id for artifact in pool.artifacts) + 1

    @staticmethod
    def _get_next_version_id(pool: Any) -> int:
        """Return the next available version id."""
        versions = pool.get_all_versions()
        if not versions:
            return 1
        return max(version.id for version in versions) + 1

    @staticmethod
    def _required_non_blank_str(value: Any, field_name: str) -> str:
        """Validate and return a required non-blank string."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"'{field_name}' must be a non-empty string.")
        return value.strip()

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        """Return a stripped optional string or None."""
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Optional string field must be a string or null.")
        stripped_value = value.strip()
        return stripped_value if stripped_value else None

    @staticmethod
    def _required_non_negative_int(value: Any, field_name: str) -> int:
        """Validate and return a required non-negative integer."""
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"'{field_name}' must be a non-negative integer.")
        return value

    @staticmethod
    def _optional_non_negative_int(value: Any, field_name: str) -> int | None:
        """Validate and return an optional non-negative integer."""
        if value is None:
            return None
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"'{field_name}' must be a non-negative integer or null.")
        return value

    @staticmethod
    def _parse_created_at(value: Any) -> datetime:
        """Parse a required created_at datetime string."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("'created_at' must be a non-empty ISO datetime string.")
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("'created_at' must be a valid ISO datetime string.") from exc

    @staticmethod
    def _parse_optional_datetime(value: Any) -> datetime | None:
        """Parse an optional ISO datetime string."""
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Optional datetime field must be a valid ISO string or null.")
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Optional datetime field must be a valid ISO string or null.") from exc

    @staticmethod
    def _resolve_frontend_dist_dir() -> Path:
        """Return the installed frontend dist directory or the local dev one."""
        installed_dist_dir = Path("/opt/coldpool/frontend/dist")
        if installed_dist_dir.is_dir():
            return installed_dist_dir

        current_file = Path(__file__).resolve()
        repo_dist_dir = current_file.parents[5] / "coldpool_web_app" / "dist"
        if repo_dist_dir.is_dir():
            return repo_dist_dir

        raise FileNotFoundError(
            "Frontend dist directory was not found in /opt/coldpool/frontend/dist " "or in the local repository build output."
        )
