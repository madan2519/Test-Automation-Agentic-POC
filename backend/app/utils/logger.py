import logging
import sys
from config.settings import settings

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

logger = setup_logger("automation_platform")
