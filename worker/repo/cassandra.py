from acsylla import create_cluster, Session
from typing import Optional
from worker.repo.base import AbstractIncidenceLogger
from worker.schemas import Incident
from uuid import UUID


class CassandraIncidenceLogger(AbstractIncidenceLogger):
    def __init__(
        self,
        keyspace: str = "surveillance",
        contact_points: Optional[list[str]] = None,
    ):
        self.keyspace = keyspace
        self.contact_points = contact_points or ["127.0.0.1"]
        self.session: Optional[Session] = None
        self._prepared_stmt = None

    async def connect(self):
        cluster = create_cluster(self.contact_points)
        self.session = await cluster.create_session()
        await self.session.set_keyspace(self.keyspace)

        self._prepared_stmt = await self.session.prepare("""
            INSERT INTO incident_annotations (
                camera_id,
                timestamp,
                label,
                confidence,
                bounding_box,
                category
            ) VALUES (?, ?, ?, ?, ?, ?)
        """)

    async def log(self, incident: Incident) -> None:
        if self.session is None:
            raise RuntimeError("Cassandra session not initialized. Call connect() first.")

        for annotation in incident.annotations:
            await self.session.execute(
                self._prepared_stmt.bind((
                    incident.camera_id,
                    incident.timestamp,
                    annotation.label,
                    annotation.confidence,
                    annotation.bounding_box,
                    annotation.category
                ))
            )

    async def flush(self) -> None:
        # Cassandra writes are immediate
        return
