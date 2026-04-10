import logging
import sys
import time
from typing import Any

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

class PipelineLogger:
    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.logger = get_logger(f"Pipeline.{stage_name}")
        self.start_time = None

    def start(self, details: str = ""):
        self.start_time = time.time()
        self.logger.info(f"STARTING stage: {self.stage_name} {details}")

    def end(self, details: str = ""):
        duration = time.time() - self.start_time if self.start_time else 0
        self.logger.info(f"COMPLETED stage: {self.stage_name} in {duration:.2f}s {details}")

    def error(self, message: str, exc: Exception = None):
        self.logger.error(f"ERROR in {self.stage_name}: {message}", exc_info=exc)

    def info(self, message: str):
        self.logger.info(message)
