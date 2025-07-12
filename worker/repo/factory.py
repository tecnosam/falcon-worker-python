


import random
from worker.repo.base import (
    AbstractIncidenceLogger,
    AbstractPubSubProvider,
    AbstractVectorStore,
)
# from worker.repo.jetstream import JetStreamPubSubProvider

from worker.repo.mocks import (
    MockIncidenceLogger,
    MockVectorStore,
    MockPubSubProvider
)
from worker.schemas import IncidentAnnotation


class Factory:

    def create_pubsub_provider(self, **kwargs) -> AbstractPubSubProvider:
        """
        Factory method to create a PubSub provider instance.

        :return: An instance of a PubSub provider.
        """

        return MockPubSubProvider(**kwargs)

        # stream_name = kwargs.get("stream_name", "DEFAULT")
        # subjects = kwargs.get("subjects", ["default.*"])

        # return JetStreamPubSubProvider(
        #     stream_name=stream_name,
        #     subjects=subjects
        # )

    def create_vector_store(self) -> AbstractVectorStore:
        """
        Factory method to create a vector store instance.

        :return: An instance of a vector store.
        """

        store = MockVectorStore()
        store.preload([
            IncidentAnnotation(
                label=random.choice([
                    "jackson smith",
                    "Tom Holland",
                    "The boogieman",
                    "Security staff 1826A"
                ]),
                confidence=round(random.uniform(0.6, 1.0), 2),
                bounding_box=[random.randint(0, 10) for _ in range(4)],
                category=random.choice(["person"]),
                embedding=[random.random() for _ in range(128)],
            )
            for _ in range(10)
        ])  # Preload with an empty list or some predefined annotations
        return store

    def create_incidence_logger(self) -> AbstractIncidenceLogger:
        """
        Factory method to create an incidence logger instance.

        :return: An instance of an incidence logger.
        """

        return MockIncidenceLogger()
