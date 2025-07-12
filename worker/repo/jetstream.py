from nats.aio.client import Client as NATS
from nats.js.client import JetStreamContext
from nats.js.api import StreamConfig
from typing import Any, Awaitable, Callable, List
import json

from .base import AbstractPubSubProvider  # Assuming your interface is in base.py


class JetStreamPubSubProvider(AbstractPubSubProvider):
    def __init__(
        self,
        stream_name: str,
        subjects: List[str],
        nats_url: str = "nats://localhost:4222",
    ):
        self.nats_url = nats_url
        self.stream_name = stream_name
        self.nc: NATS = NATS()
        self.js: JetStreamContext = self.nc.jetstream()
        self.subjects = subjects

    async def connect(self):
        if not self.nc.is_connected:
            await self.nc.connect(servers=[self.nats_url])

            # Create the stream (if not already present)
            try:
                await self.js.add_stream(
                    name=self.stream_name,
                    config=StreamConfig(
                        name=self.stream_name,
                        subjects=self.subjects,
                        retention="limits",
                        max_msgs=100_000,
                        max_age=3600 * 12,  # 12 hours
                        storage="memory",
                        discard="old"
                    )
                )
            except Exception as e:
                if "already in use" not in str(e).lower():
                    raise

    async def publish(self, channel: str, message: Any):
        if not self.js:
            await self.connect()

        payload = json.dumps(message).encode("utf-8")
        await self.js.publish(subject=channel, payload=payload)

    async def subscribe(self, channel: str, callback: Callable[[str], Awaitable[None]]):
        if not self.js:
            await self.connect()

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode("utf-8"))
                await callback(data)
                await msg.ack()
            except Exception as e:
                print(f"[JetStream] Error in message handler: {e}")

        await self.js.subscribe(
            subject=channel,
            durable=f"durable-{channel.replace('.', '_')}",
            cb=message_handler,
            stream=self.stream_name,
            manual_ack=True,
        )
