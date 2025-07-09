import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str = "competitive_analysis",
    log_file: str = "competitive_analysis.log",
    log_level: str = "INFO",
    max_size: str = "10MB",
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up a comprehensive logging system for the application
    
    Args:
        name: Logger name
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_size: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        console_output: Whether to output logs to console
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Convert size string to bytes
        size_bytes = _parse_size(max_size)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=size_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Create a separate error log file
    error_log_file = log_file.replace('.log', '_errors.log') if log_file else 'errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=size_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # Log the logger setup
    logger.info(f"Logger '{name}' initialized with level {log_level}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Error log file: {error_log_file}")
    
    return logger

def _parse_size(size_str: str) -> int:
    """
    Parse size string (e.g., '10MB', '1GB') to bytes
    
    Args:
        size_str: Size string with unit
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper()
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
    }
    
    for unit, multiplier in multipliers.items():
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
            except ValueError:
                pass
    
    # Default to 10MB if parsing fails
    return 10 * 1024 * 1024

def log_function_call(func):
    """
    Decorator to log function calls with parameters and results
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("competitive_analysis")
        
        # Log function entry
        logger.debug(f"Entering {func.__name__} with args: {args}, kwargs: {kwargs}")
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Log successful completion
            logger.debug(f"Completed {func.__name__} successfully")
            
            return result
            
        except Exception as e:
            # Log error
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper

def log_execution_time(func):
    """
    Decorator to log function execution time
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("competitive_analysis")
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    return wrapper

class LoggerContext:
    """Context manager for temporary logger configuration"""
    
    def __init__(self, logger_name: str = "competitive_analysis", level: str = "DEBUG"):
        self.logger = logging.getLogger(logger_name)
        self.original_level = self.logger.level
        self.new_level = getattr(logging, level.upper())
    
    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)

def get_logger(name: str = "competitive_analysis") -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_system_info():
    """Log system information for debugging purposes"""
    logger = logging.getLogger("competitive_analysis")
    
    import platform
    
    logger.info("=== System Information ===")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python Version: {platform.python_version()}")
    
    try:
        import psutil
        logger.info(f"CPU Count: {psutil.cpu_count()}")
        logger.info(f"Memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")
        logger.info(f"Available Memory: {psutil.virtual_memory().available / (1024**3):.2f} GB")
    except ImportError:
        logger.info("psutil not available - skipping memory information")
    
    logger.info("=== End System Information ===")

def log_configuration(config):
    """
    Log configuration settings (excluding sensitive information)
    
    Args:
        config: Configuration object
    """
    logger = logging.getLogger("competitive_analysis")
    
    logger.info("=== Configuration Settings ===")
    
    # Log non-sensitive configuration
    safe_config = {
        "max_search_results": config.max_search_results,
        "request_timeout": config.request_timeout,
        "rate_limit_delay": config.rate_limit_delay,
        "model_name": config.model_name,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "debug_mode": config.debug_mode,
        "output_directory": config.output_directory,
        "data_directory": config.data_directory
    }
    
    for key, value in safe_config.items():
        logger.info(f"{key}: {value}")
    
    # Log API key status (without revealing the keys)
    logger.info(f"OpenAI API Key: {'Set' if config.openai_api_key else 'Not Set'}")
    logger.info(f"Google API Key: {'Set' if config.google_api_key else 'Not Set'}")
    
    logger.info("=== End Configuration Settings ===")

# Initialize default logger when module is imported
default_logger = setup_logger() 