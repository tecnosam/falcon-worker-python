import sys
import asyncio
import queue
from uuid import UUID

from worker import (
    poll_image_queue_and_publish,
    camera_worker
)
from worker.consumers import get_incident_handler
from worker.repo.factory import Factory
from worker.settings import WorkerConfig


async def main(camera_id: UUID, config: WorkerConfig):
    """
    Main entry point for the worker.
    """

    factory = Factory()
    image_queue = queue.Queue()
    incident_logger = factory.create_incidence_logger()
    vector_store = factory.create_vector_store()
    camera_repo = factory.create_camera_repo()

    # Create and connect pubsub providers
    incidents_pubsub = factory.create_pubsub_provider(
        stream_name="INCIDENTS",
        subjects=["incident.*"]
    )
    frames_pubsub = factory.create_pubsub_provider(
        stream_name="FRAMES",
        subjects=["frames.*"]
    )

    await incidents_pubsub.connect()
    await frames_pubsub.connect()

    # Start incident subscription
    incident_channel = f"incident.{camera_id}"
    subscriber_task = incidents_pubsub.subscribe(
        channel=incident_channel,
        callback=get_incident_handler(
            channel=incident_channel,
            logger=incident_logger,
            vector_store=vector_store,
            camera_repo=camera_repo
        )
    )

    # Start camera stream reader
    camera_thread = asyncio.to_thread(
        camera_worker,
        rtsp_url=camera_repo.get_connection_info(camera_id=camera_id),
        camera_id=camera_id,
        image_queue=image_queue,
    )

    print(f"[worker] Starting worker for camera: {camera_id}")

    await asyncio.gather(
        camera_thread,
        poll_image_queue_and_publish(
            q=image_queue,
            pubsub=frames_pubsub,
            channel=config.image_write_channel
        ),
        subscriber_task
    )


if __name__ == "__main__":
    if sys.argv[1:]:
        camera_id = UUID(sys.argv[1])
    else:
        print("Usage: python -m worker <camera_id>")
        sys.exit(1)

    asyncio.run(main(camera_id=camera_id, config=WorkerConfig()))
