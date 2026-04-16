from __future__ import annotations

from datetime import datetime
from typing import Any

from coldpool_server.artifact.artifact import Artifact
from coldpool_server.artifact.artifact_copy import ArtifactCopy
from coldpool_server.artifact.artifact_version import ArtifactVersion
from coldpool_server.database.database_connector import DatabaseConnector
from coldpool_server.disk.disk import Disk
from coldpool_server.pool.pool import Pool


class PoolLoader:
    """Load and dump a Pool from and to the SQLite database."""

    current_pool: Pool | None = None

    @classmethod
    def get_current_pool(cls) -> Pool:
        """Return the cached pool, loading it from SQLite if needed."""
        if cls.current_pool is None:
            cls.current_pool = cls._load_pool_from_database()
        return cls.current_pool

    @classmethod
    def invalidate_current_pool(cls) -> None:
        """Invalidate the cached pool so the next access reloads from SQLite."""
        cls.current_pool = None

    @classmethod
    def reload_current_pool(cls) -> Pool:
        """Force a reload from SQLite and return the new pool."""
        cls.invalidate_current_pool()
        return cls.get_current_pool()

    @classmethod
    def load_pool(cls) -> Pool:
        """Backward-compatible alias for get_current_pool."""
        return cls.get_current_pool()

    @classmethod
    def _load_pool_from_database(cls) -> Pool:
        """Load the full connected Pool object graph from SQLite."""
        disk_rows = DatabaseConnector.execute_query(
            """
            SELECT
                id,
                name,
                total_capacity_bytes,
                health_score,
                location,
                state
            FROM disks
            ORDER BY id
            """,
            [],
        )

        artifact_rows = DatabaseConnector.execute_query(
            """
            SELECT
                id,
                name,
                priority_score,
                desired_copy_count,
                artifact_type,
                shelf_life_days
            FROM artifacts
            ORDER BY id
            """,
            [],
        )

        version_rows = DatabaseConnector.execute_query(
            """
            SELECT
                id,
                artifact_id,
                version_label,
                created_at,
                size_bytes,
                checksum,
                expires_at
            FROM artifact_versions
            ORDER BY id
            """,
            [],
        )

        copy_rows = DatabaseConnector.execute_query(
            """
            SELECT
                id,
                artifact_version_id,
                copy_index,
                disk_id,
                disk_path,
                is_present,
                status
            FROM copies
            ORDER BY id
            """,
            [],
        )

        disks: list[Disk] = []
        disk_by_id: dict[int, Disk] = {}

        for row in disk_rows:
            disk = Disk(
                id=cls._row_value(row, "id", 0),
                name=cls._row_value(row, "name", 1),
                total_capacity_bytes=cls._row_value(row, "total_capacity_bytes", 2),
                health_score=cls._row_value(row, "health_score", 3),
                location=cls._row_value(row, "location", 4),
                state=cls._row_value(row, "state", 5),
                copies=[],
            )
            disks.append(disk)
            disk_by_id[disk.id] = disk

        artifacts: list[Artifact] = []
        artifact_by_id: dict[int, Artifact] = {}

        for row in artifact_rows:
            artifact = Artifact(
                id=cls._row_value(row, "id", 0),
                name=cls._row_value(row, "name", 1),
                priority_score=cls._row_value(row, "priority_score", 2),
                desired_copy_count=cls._row_value(row, "desired_copy_count", 3),
                artifact_type=cls._row_value(row, "artifact_type", 4),
                shelf_life_days=cls._row_value(row, "shelf_life_days", 5),
            )
            artifacts.append(artifact)
            artifact_by_id[artifact.id] = artifact

        version_by_id: dict[int, ArtifactVersion] = {}

        for row in version_rows:
            artifact_id = cls._row_value(row, "artifact_id", 1)
            artifact_or_none = artifact_by_id.get(artifact_id)
            if artifact_or_none is None:
                raise ValueError(f"Database contains artifact_version referencing missing artifact_id={artifact_id}.")
            artifact = artifact_or_none

            expires_at_raw = cls._row_value(row, "expires_at", 6)

            version = ArtifactVersion(
                id=cls._row_value(row, "id", 0),
                artifact=artifact,
                version_label=cls._row_value(row, "version_label", 2),
                created_at=datetime.fromisoformat(cls._row_value(row, "created_at", 3)),
                size_bytes=cls._row_value(row, "size_bytes", 4),
                checksum=cls._row_value(row, "checksum", 5),
                expires_at=(datetime.fromisoformat(expires_at_raw) if expires_at_raw is not None else None),
                copies=[],
            )
            artifact.add_version(version)
            version_by_id[version.id] = version

        for row in copy_rows:
            artifact_version_id = cls._row_value(row, "artifact_version_id", 1)
            disk_id = cls._row_value(row, "disk_id", 3)

            artifact_version_or_none = version_by_id.get(artifact_version_id)
            if artifact_version_or_none is None:
                raise ValueError("Database contains copy referencing missing " f"artifact_version_id={artifact_version_id}.")
            artifact_version = artifact_version_or_none

            disk_or_none = disk_by_id.get(disk_id)
            if disk_or_none is None:
                raise ValueError(f"Database contains copy referencing missing disk_id={disk_id}.")
            disk = disk_or_none

            artifact_copy = ArtifactCopy(
                id=cls._row_value(row, "id", 0),
                artifact_version=artifact_version,
                copy_index=cls._row_value(row, "copy_index", 2),
                disk=disk,
                disk_path=cls._row_value(row, "disk_path", 4),
                is_present=bool(cls._row_value(row, "is_present", 5)),
                status=cls._row_value(row, "status", 6),
            )

            artifact_version.add_copy(artifact_copy)
            disk.add_copy(artifact_copy)

        return Pool(
            disks=disks,
            artifacts=artifacts,
        )

    @classmethod
    def dump_pool(cls, pool: Pool) -> None:
        """Persist the full Pool object graph into SQLite and invalidate cache.

        The pool is treated as the source of truth:
        - rows present in the pool are inserted or updated
        - rows missing from the pool are deleted
        - the in-memory cache is invalidated, so the next read reloads from DB
        """
        cls._upsert_disks(pool)
        cls._upsert_artifacts(pool)
        cls._upsert_versions(pool)
        cls._upsert_copies(pool)

        cls._delete_missing_copies(pool)
        cls._delete_missing_versions(pool)
        cls._delete_missing_artifacts(pool)
        cls._delete_missing_disks(pool)

        cls.invalidate_current_pool()

    @classmethod
    def _upsert_disks(cls, pool: Pool) -> None:
        for disk in pool.disks:
            DatabaseConnector.execute_query(
                """
                INSERT INTO disks (
                    id,
                    name,
                    total_capacity_bytes,
                    health_score,
                    location,
                    state
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    total_capacity_bytes = excluded.total_capacity_bytes,
                    health_score = excluded.health_score,
                    location = excluded.location,
                    state = excluded.state
                """,
                [
                    disk.id,
                    disk.name,
                    disk.total_capacity_bytes,
                    disk.health_score,
                    disk.location,
                    disk.state,
                ],
            )

    @classmethod
    def _upsert_artifacts(cls, pool: Pool) -> None:
        for artifact in pool.artifacts:
            DatabaseConnector.execute_query(
                """
                INSERT INTO artifacts (
                    id,
                    name,
                    priority_score,
                    desired_copy_count,
                    artifact_type,
                    shelf_life_days
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    priority_score = excluded.priority_score,
                    desired_copy_count = excluded.desired_copy_count,
                    artifact_type = excluded.artifact_type,
                    shelf_life_days = excluded.shelf_life_days
                """,
                [
                    artifact.id,
                    artifact.name,
                    artifact.priority_score,
                    artifact.desired_copy_count,
                    artifact.artifact_type,
                    artifact.shelf_life_days,
                ],
            )

    @classmethod
    def _upsert_versions(cls, pool: Pool) -> None:
        for version in pool.get_all_versions():
            DatabaseConnector.execute_query(
                """
                INSERT INTO artifact_versions (
                    id,
                    artifact_id,
                    version_label,
                    created_at,
                    size_bytes,
                    checksum,
                    expires_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    artifact_id = excluded.artifact_id,
                    version_label = excluded.version_label,
                    created_at = excluded.created_at,
                    size_bytes = excluded.size_bytes,
                    checksum = excluded.checksum,
                    expires_at = excluded.expires_at
                """,
                [
                    version.id,
                    version.artifact.id,
                    version.version_label,
                    version.created_at.isoformat(),
                    version.size_bytes,
                    version.checksum,
                    version.expires_at.isoformat() if version.expires_at is not None else None,
                ],
            )

    @classmethod
    def _upsert_copies(cls, pool: Pool) -> None:
        for artifact_copy in pool.get_all_copies():
            DatabaseConnector.execute_query(
                """
                INSERT INTO copies (
                    id,
                    artifact_version_id,
                    copy_index,
                    disk_id,
                    disk_path,
                    is_present,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    artifact_version_id = excluded.artifact_version_id,
                    copy_index = excluded.copy_index,
                    disk_id = excluded.disk_id,
                    disk_path = excluded.disk_path,
                    is_present = excluded.is_present,
                    status = excluded.status
                """,
                [
                    artifact_copy.id,
                    artifact_copy.artifact_version.id,
                    artifact_copy.copy_index,
                    artifact_copy.disk.id,
                    artifact_copy.disk_path,
                    1 if artifact_copy.is_present else 0,
                    artifact_copy.status,
                ],
            )

    @classmethod
    def _delete_missing_copies(cls, pool: Pool) -> None:
        pool_copy_ids = [artifact_copy.id for artifact_copy in pool.get_all_copies()]
        cls._delete_missing_ids(
            table_name="copies",
            id_list=pool_copy_ids,
        )

    @classmethod
    def _delete_missing_versions(cls, pool: Pool) -> None:
        pool_version_ids = [version.id for version in pool.get_all_versions()]
        cls._delete_missing_ids(
            table_name="artifact_versions",
            id_list=pool_version_ids,
        )

    @classmethod
    def _delete_missing_artifacts(cls, pool: Pool) -> None:
        pool_artifact_ids = [artifact.id for artifact in pool.artifacts]
        cls._delete_missing_ids(
            table_name="artifacts",
            id_list=pool_artifact_ids,
        )

    @classmethod
    def _delete_missing_disks(cls, pool: Pool) -> None:
        pool_disk_ids = [disk.id for disk in pool.disks]
        cls._delete_missing_ids(
            table_name="disks",
            id_list=pool_disk_ids,
        )

    @classmethod
    def _delete_missing_ids(
        cls,
        table_name: str,
        id_list: list[int],
    ) -> None:
        """Delete rows whose id is not present in id_list."""
        if not id_list:
            DatabaseConnector.execute_query(
                f"DELETE FROM {table_name}",
                [],
            )
            return

        placeholders = ", ".join(["?"] * len(id_list))
        DatabaseConnector.execute_query(
            f"DELETE FROM {table_name} WHERE id NOT IN ({placeholders})",
            id_list,
        )

    @staticmethod
    def _row_value(row: Any, column_name: str, column_index: int) -> Any:
        """Read a value from a DB row supporting sqlite3.Row or tuple-like rows."""
        try:
            return row[column_name]
        except (TypeError, KeyError, IndexError):
            return row[column_index]
