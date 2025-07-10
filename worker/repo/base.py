from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Any, Awaitable

from worker.schemas import Incident, IncidentAnnotation


class AbstractIncidenceLogger(ABC):
    """
    Abstract base class for incidence loggers.
    """

    @abstractmethod
    async def log(self, incidence: Incident) -> None:
        """
        Log an incidence with the given message.
        
        :param message: The message to log.
        """
        pass

    @abstractmethod
    async def flush(self) -> None:
        """
        Flush the log, ensuring all messages are written out.
        """
        pass


class AbstractVectorStore(ABC):
    """
    Abstract base class for vector stores.
    """

    @abstractmethod
    async def get_top_k_similar_annotations(
        self,
        collection: str,
        embedding: List[float],
        dimensions: List[int],
        bounding_box: List[int],
        k: int = 5,
        **filters
    ) -> list[IncidentAnnotation]:
        """
        Get the top k similar annotations from the vector store.
        
        :param collection: The name of the collection to search in.
        :param embedding: The embedding vector to search for.
        :param dimensions: The dimensions of the embedding.
        :param bounding_box: The bounding box of the subject of the incidence
        :param k: The number of similar annotations to return.
        :param filters: Additional filters to apply to the search.
        :return: A list of annotations.
        """
        pass


class AbstractCameraRepo(ABC):
    """
    Abstract base class for camera repositories.
    """

    @abstractmethod
    async def get_connection_info(self, camera_id: UUID) -> Any:
        """
        Get the connection information for a camera.
        
        :param camera_id: The ID of the camera.
        :return: Workable connection information
        """
        pass

    @abstractmethod
    async def get_camera_owner_id(self, camera_id: UUID) -> UUID:
        """
        Get the owner ID of a camera.
        
        :param camera_id: The ID of the camera.
        :return: The owner ID of the camera.
        """
        pass


class AbstractPubSubProvider(ABC):

    @abstractmethod
    async def subscribe(
        self,
        channel: str,
        callback: Awaitable
    ):
        """
        Subscribes to a channel / topic on a PubSub

        :param channel: Channel to subscribe to 
        :param callback: Function to run when a new message is received

        :returns: A coroutine that continuously listens to messages and calls callback
        """

    @abstractmethod
    async def publish(self, channel: str, message: Any):
        """
        Publish a message to a channel.

        :param channel: Channel to send message to
        :param message: Message to be transmitted
        """
