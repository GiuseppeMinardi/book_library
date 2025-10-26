from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from .logger_config import LoggerConfig

_config = LoggerConfig()

# Application-wide logger
logger = logging.getLogger(_config.logger_name)

logger.setLevel(_config.log_level)

file_handler = logging.FileHandler(_config.log_file, encoding="utf-8")
file_fmt = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s"
)
file_handler.setFormatter(file_fmt)
file_handler.setLevel(_config.log_level)
logger.addHandler(file_handler)

# Add a stream handler to print logs to stdout using the same formatter/level.
# Guard against adding multiple stdout handlers when the module is imported multiple times.
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(file_fmt)
stream_handler.setLevel(_config.log_level)
if not any(
    isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout
    for h in logger.handlers
):
    logger.addHandler(stream_handler)

# Prevent messages from being propagated to the root logger to avoid duplicates
logger.propagate = False

__all__ = ["logger"]

