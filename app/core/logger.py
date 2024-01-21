"""App logger module."""

import logging
import sys

from app.core import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
