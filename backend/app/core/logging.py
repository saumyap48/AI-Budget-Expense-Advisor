import os
import logging
import sys

# Ensure logs directory exists
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

APP_LOG_PATH = os.path.join(LOGS_DIR, "app.log")
ERROR_LOG_PATH = os.path.join(LOGS_DIR, "error.log")
AI_LOG_PATH = os.path.join(LOGS_DIR, "ai.log")
REQUEST_LOG_PATH = os.path.join(LOGS_DIR, "request.log")

formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# App Logger
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(APP_LOG_PATH)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Error Logger
error_logger = logging.getLogger("error")
error_logger.setLevel(logging.ERROR)
error_file_handler = logging.FileHandler(ERROR_LOG_PATH)
error_file_handler.setFormatter(formatter)
error_logger.addHandler(error_file_handler)
error_logger.addHandler(console_handler)

# AI Logger
ai_logger = logging.getLogger("ai")
ai_logger.setLevel(logging.INFO)
ai_file_handler = logging.FileHandler(AI_LOG_PATH)
ai_file_handler.setFormatter(formatter)
ai_logger.addHandler(ai_file_handler)

# Request Logger
request_logger = logging.getLogger("request")
request_logger.setLevel(logging.INFO)
req_file_handler = logging.FileHandler(REQUEST_LOG_PATH)
req_file_handler.setFormatter(formatter)
request_logger.addHandler(req_file_handler)
