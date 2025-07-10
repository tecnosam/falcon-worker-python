

class WorkerConfig:
    """
    Application settings for the Falcon Worker.
    """
    
    image_write_channel: str = "image.raw"
    video_write_channel: str = "video.raw"
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Other application-specific settings can be added here
