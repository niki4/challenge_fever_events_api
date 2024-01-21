"""App settings."""

import os


DEBUG = os.getenv("DEBUG", "")
DEFAULT_REQUEST_TIMEOUT = 60  # 1 minute
EVENT_PROVIDER_URL = "https://provider.code-challenge.feverup.com/api/events"
