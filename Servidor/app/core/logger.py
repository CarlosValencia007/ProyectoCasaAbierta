"""
Smart Classroom AI - Logging Configuration
Structured logging with context tracking
"""
import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logger(name: str = "smart_classroom") -> logging.Logger:
    """Configure and return logger instance"""
    
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # File handler (optional, for production)
    if settings.ENVIRONMENT == "production":
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
