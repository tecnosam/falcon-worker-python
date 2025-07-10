
from worker.repo.base import AbstractIncidenceLogger, AbstractVectorStore


def get_incident_handler(
    channel: str,
    logger: AbstractIncidenceLogger,
    vector_store: AbstractVectorStore,
):

    async def handle_incident(incident):
        """
        Handle an incident by processing its annotations and storing them in a vector store.
        
        :param incident: The incident to handle, containing annotations and other metadata.
        """

    return handle_incident
