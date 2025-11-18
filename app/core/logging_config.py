import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal


_configured = False


def setup_logging(
    log_level: Literal[
        "CRITICAL",
        "ERROR",
        "WARNING",
        "INFO",
        "DEBUG",
        "NOTSET",
    ] = "ERROR",
    log_file: str = "logs/app.log",
) -> None:
    global _configured
    if _configured:
        return

    # Ensure directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, log_level.upper(), logging.ERROR)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s (%(pathname)s:%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicating handlers in reload
    has_same = any(
        isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == str(log_path)
        for h in root.handlers
    )
    if not has_same:
        root.addHandler(file_handler)

    _configured = True

