from time import time
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class IncidentAnnotation(BaseModel):
    """
    Represents an annotation for an incident.
    """
    label: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)  # Confidence score between 0 and 1
    bounding_box: List[float] = Field(default_factory=list)  # [x_min, y_min, x_max, y_max]
    category: str = None  # Optional category for the annotation


class Incident(BaseModel):

    frame_id: UUID
    camera_id: UUID
    timestamp: float
    annotations: List[IncidentAnnotation]
    embedding: List[float] = None
    dimensions: List[int] = None


class BaseFrame(BaseModel):
    """
    Base class for frames,
    containing common attributes for both image and video frames.
    """
    frame_id: UUID = Field(default_factory=uuid4)  # Unique identifier for the frame
    camera_id: UUID
    timestamp: float = Field(default_factory=time.time)
    dimensions: List[int] = Field(default_factory=list)  # [width, height]
    encoding: str = "jpeg"  # Default encoding format


class ImageFrame(BaseFrame):
    """
    Represents an image frame with its associated metadata.
    """

    image_data: bytes  # Raw image data
    encoding: str = "jpeg"  # Default encoding format


class VideoFrame(BaseModel):
    """
    Represents a video frame with its associated metadata.
    """

    video_data: bytes  # Raw video data
    encoding: str = "mp4"  # Default encoding format
    frame_rate: float = 30.0  # Default frame rate in frames per second