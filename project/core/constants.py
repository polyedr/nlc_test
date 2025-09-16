"""Project-wide constants used across models, views, tasks and admin."""

# Pagination
DEFAULT_PAGE_SIZE: int = 5
MAX_PAGE_SIZE: int = 100

# Allowed content types for PageContent
APP_LABEL_CORE: str = "core"
MODEL_VIDEO: str = "video"
MODEL_AUDIO: str = "audio"
ALLOWED_CONTENT_MODELS: tuple[str, ...] = (MODEL_VIDEO, MODEL_AUDIO)

# Seed/demo defaults
CDN_VIDEO_BASE: str = "https://cdn.example.com/videos"
CDN_SUBS_BASE: str = "https://cdn.example.com/subtitles"

# API types
ITEM_TYPE_VIDEO: str = "video"
ITEM_TYPE_AUDIO: str = "audio"
