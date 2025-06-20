# Structured JSON logging for failures (Promtail picks up ui_render.log)
import logging
import os
from pythonjsonlogger import jsonlogger

LOG_FILE = os.getenv("UI_LOG_PATH", "/app/logs/ui_render.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logger = logging.getLogger("ui-render-logger")
logger.setLevel(logging.INFO)

fh = logging.FileHandler(LOG_FILE)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s'
)
fh.setFormatter(formatter)
logger.addHandler(fh)

def log_failure(endpoint: str, url: str, error: str, run_id: str, tags: dict):
    logger.error(
        "render_failure",
        extra={
            "endpoint": endpoint,
            "url": url,
            "error": error,
            "run_id": run_id,
            **tags
        }
    )

def log_success(endpoint: str, url: str, render_time: float, tags: dict):
    logger.info(
        "render_success",
        extra={
            "endpoint": endpoint,
            "url": url,
            "render_time": render_time,
            **tags
        }
    )
