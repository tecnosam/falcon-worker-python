from itertools import chain
import asyncio
from collections import defaultdict
import json
from typing import Mapping
from worker.repo.base import AbstractIncidenceLogger, AbstractVectorStore
from worker.schemas import Incident, IncidentAnnotation


def get_incident_handler(
    channel: str,
    logger: AbstractIncidenceLogger,
    vector_store: AbstractVectorStore,
):

    async def handle_incident(message: str) -> None:
        """
        Handle an incident by processing its annotations and storing them in a vector store.
        
        :param incident: The incident to handle, containing annotations and other metadata.
        """

        incident = json.loads(message)
        incident = Incident(**incident)


        collections: Mapping[str, list[IncidentAnnotation]] = defaultdict(lambda: [])

        for annotation in incident.annotations:
            if annotation.category is None:
                continue
            collections[annotation.category].append(annotation)

        for collection, collection_annotations in collections.items():

            search_tasks = [
                vector_store.get_top_k_similar_annotations(
                    collection=collection,
                    embedding=annotation.embedding,
                    dimensions=incident.dimensions,
                    bounding_box=annotation.bounding_box,
                    min_distance=0.5,
                    k=1,
                )
                for annotation in collection_annotations
            ]

            additional_annotations = list(chain.from_iterable(
                await asyncio.gather(*search_tasks)
            ))

            if additional_annotations:
                print(
                    f"Found {len(additional_annotations)} similar"
                    f" annotations in {collection} for incident {incident.camera_id}"
                )
                incident.annotations.extend(additional_annotations)

        # Log the incident
        await logger.log(incident)

    return handle_incident
