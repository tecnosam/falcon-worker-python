
import asyncio
import cv2
import queue

from uuid import UUID

import numpy as np

from worker.schemas import ImageFrame

from worker.repo.base import AbstractPubSubProvider


def camera_worker(
    rtsp_url: str,
    camera_id: UUID,
    image_queue: queue.Queue,
):

    cap = cv2.VideoCapture(0 if rtsp_url == "0" else rtsp_url)

    last_frame = None
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            _, buffer = cv2.imencode('.jpg', frame)

            # Stops worker from queueing static images
            if last_frame is not None and np.allclose(frame, last_frame, atol=10):
                continue
            last_frame = frame.copy()

            image_frame = ImageFrame(
                camera_id=camera_id,
                image_data=buffer.tobytes(),
                dimensions=[*frame.shape]
            )
            image_queue.put(image_frame)
    finally:
        cap.release()
        cv2.destroyAllWindows()


async def poll_image_queue_and_publish(
    q: queue.Queue,
    pubsub: AbstractPubSubProvider,
    channel: str,
):
    loop = asyncio.get_running_loop()

    while True:
        # Pull blocking queue item in a thread-safe way
        image_frame: ImageFrame = await loop.run_in_executor(None, q.get)

        # TODO: implement a background task manager
        asyncio.create_task(pubsub.publish(channel, image_frame))
