


from worker.repo.base import AbstractIncidenceLogger, AbstractPubSubProvider, AbstractVectorStore
from worker.repo.jetstream import JetStreamPubSubProvider


class Factory:

    def create_pubsub_provider(self, **kwargs) -> AbstractPubSubProvider:
        """
        Factory method to create a PubSub provider instance.

        :return: An instance of a PubSub provider.
        """

        stream_name = kwargs.get("stream_name", "DEFAULT")
        subjects = kwargs.get("subjects", ["default.*"])

        return JetStreamPubSubProvider(
            stream_name=stream_name,
            subjects=subjects
        )

    def create_vector_store(self) -> AbstractVectorStore:
        """
        Factory method to create a vector store instance.

        :return: An instance of a vector store.
        """

    def create_incidence_logger(self) -> AbstractIncidenceLogger:
        """
        Factory method to create an incidence logger instance.

        :return: An instance of an incidence logger.
        """
