
import asyncio
import random
import time
from typing import Any, Awaitable, Callable, List
from uuid import uuid4
from worker.schemas import Incident, IncidentAnnotation
from worker.repo.base import AbstractIncidenceLogger, AbstractVectorStore, AbstractPubSubProvider


class MockIncidenceLogger(AbstractIncidenceLogger):
    def __init__(self):
        self.logged = []

    async def log(self, incidence: Incident) -> None:
        self.logged.append(incidence)

    async def flush(self) -> None:
        # No-op or simulate sending to storage
        pass


class MockVectorStore(AbstractVectorStore):
    def __init__(self):
        self.storage = []  # could be List[IncidentAnnotation]

    async def get_top_k_similar_annotations(
        self,
        collection: str,
        embedding: List[float],
        dimensions: List[int],
        bounding_box: List[int],
        k: int = 5,
        **filters
    ) -> List[IncidentAnnotation]:
        # Return the first k annotations regardless of embedding similarity
        return self.storage[:k]

    def preload(self, annotations: List[IncidentAnnotation]):
        self.storage.extend(annotations)


class MockPubSubProvider(AbstractPubSubProvider):
    def __init__(self, interval: float = 1.0, **kwargs):
        """
        :param interval: Seconds between published messages.
        """
        self.interval = interval
        self.active = True

    async def subscribe(
        self,
        channel: str,
        callback: Callable[[str], Awaitable[None]]
    ):
        """
        Starts an infinite loop that periodically sends a JSON string
        representing a randomly generated Incident to the callback.
        """
        while self.active:
            incident = self._generate_random_incident()
            payload = incident.model_dump_json()
            await callback(payload)
            await asyncio.sleep(self.interval)

    async def publish(self, channel: str, message: Any):
        # Not needed for test simulation, but required by interface
        pass

    def stop(self):
        """Stops the loop if needed in tests."""
        self.active = False

    def _generate_random_incident(self) -> Incident:
        return Incident(
            frame_id=uuid4(),
            camera_id=uuid4(),
            timestamp=time.time(),
            annotations=[
                IncidentAnnotation(
                    label=random.choice(["person", "vehicle", "animal"]),
                    confidence=round(random.uniform(0.6, 1.0), 2),
                    bounding_box=[random.uniform(0, 1) for _ in range(4)],
                    category=random.choice(["threat", "non-threat", None]),
                )
            ],
            embedding=[random.random() for _ in range(128)],
            dimensions=[1920, 1080],
        )
