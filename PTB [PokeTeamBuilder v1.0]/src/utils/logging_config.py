"""
Enhanced logging configuration for Pokemon Team Builder.
Provides structured logging with multiple handlers and formatters.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

try:
    from rich.logging import RichHandler as RichLoggingHandler
    from rich.console import Console as RichConsole
    RICH_AVAILABLE = True
except ImportError:
    RichLoggingHandler = None  # type: ignore
    RichConsole = None  # type: ignore
    RICH_AVAILABLE = False

try:
    import colorama
    from colorama import Fore, Style
    colorama.init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support."""
    
    COLORS = {
        'DEBUG': Fore.CYAN if COLORAMA_AVAILABLE else '',
        'INFO': Fore.GREEN if COLORAMA_AVAILABLE else '',
        'WARNING': Fore.YELLOW if COLORAMA_AVAILABLE else '',
        'ERROR': Fore.RED if COLORAMA_AVAILABLE else '',
        'CRITICAL': Fore.MAGENTA if COLORAMA_AVAILABLE else '',
    }
    
    RESET = Style.RESET_ALL if COLORAMA_AVAILABLE else ''
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.name = f"{Fore.BLUE if COLORAMA_AVAILABLE else ''}{record.name}{self.RESET}"
        return super().format(record)

class PTBLogger:
    """Pokemon Team Builder logging manager."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path(__file__).parent.parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Create log files
        self.main_log = self.log_dir / "ptb.log"
        self.error_log = self.log_dir / "errors.log"
        self.performance_log = self.log_dir / "performance.log"
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration."""
        # Root logger
        root_logger = logging.getLogger()
        root_logger.handlers.clear()  # Clear any existing handlers
        root_logger.setLevel(logging.DEBUG)
        
        # Console handler with rich formatting if available
        if RICH_AVAILABLE and RichLoggingHandler is not None and RichConsole is not None:
            console_handler = RichLoggingHandler(
                console=RichConsole(stderr=True),
                show_time=True,
                show_path=False,
                rich_tracebacks=True
            )
            console_handler.setLevel(logging.INFO)
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Use colored formatter if colorama is available
            if COLORAMA_AVAILABLE:
                console_formatter = ColoredFormatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S'
                )
            else:
                console_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S'
                )
            
            console_handler.setFormatter(console_formatter)
        
        root_logger.addHandler(console_handler)
        
        # File handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            self.main_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Error-only file handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.error_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
        
        # Performance logger
        perf_logger = logging.getLogger('performance')
        perf_handler = logging.handlers.RotatingFileHandler(
            self.performance_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        perf_handler.setLevel(logging.INFO)
        perf_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        perf_handler.setFormatter(perf_formatter)
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        perf_logger.propagate = False  # Don't propagate to root logger
        
        # Set specific logger levels
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('PIL').setLevel(logging.WARNING)
        
        # Log startup message
        main_logger = logging.getLogger('ptb.startup')
        main_logger.info("="*60)
        main_logger.info("Pokemon Team Builder v1.0 - Logging Initialized")
        main_logger.info(f"Log directory: {self.log_dir}")
        main_logger.info(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        main_logger.info("="*60)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance with the specified name."""
        return logging.getLogger(name)
    
    def log_system_info(self):
        """Log system information."""
        import platform
        import sys
        
        logger = self.get_logger('ptb.system')
        logger.info("System Information:")
        logger.info(f"  Platform: {platform.platform()}")
        logger.info(f"  Python: {sys.version}")
        logger.info(f"  Architecture: {platform.architecture()}")
        logger.info(f"  Processor: {platform.processor()}")
        
        try:
            import psutil
            memory = psutil.virtual_memory()
            logger.info(f"  Total Memory: {memory.total // 1024 // 1024 // 1024}GB")
            logger.info(f"  Available Memory: {memory.available // 1024 // 1024 // 1024}GB")
        except ImportError:
            logger.debug("psutil not available for memory info")
    
    def log_performance_metric(self, operation: str, duration: float, **kwargs):
        """Log a performance metric."""
        perf_logger = logging.getLogger('performance')
        extra_info = ' '.join([f"{k}={v}" for k, v in kwargs.items()])
        perf_logger.info(f"PERF: {operation} duration={duration:.3f}s {extra_info}")
    
    def log_user_action(self, action: str, details: str = "", user_id: str = "default"):
        """Log user actions for analytics."""
        action_logger = logging.getLogger('ptb.actions')
        action_logger.info(f"USER_ACTION: user={user_id} action={action} details={details}")
    
    def log_error_with_context(self, error: Exception, context: Optional[dict] = None):
        """Log error with additional context."""
        error_logger = logging.getLogger('ptb.errors')
        error_logger.error(f"Error: {type(error).__name__}: {error}")
        
        if context:
            for key, value in context.items():
                error_logger.error(f"  {key}: {value}")
        
        # Log stack trace
        import traceback
        error_logger.error("Stack trace:")
        for line in traceback.format_exc().splitlines():
            error_logger.error(f"  {line}")

def setup_logging(log_level: str = "INFO", log_dir: Optional[Path] = None) -> PTBLogger:
    """Setup logging for the entire application."""
    ptb_logger = PTBLogger(log_dir)
    
    # Set root logger level
    numeric_level = getattr(logging, log_level.upper(), None)
    if isinstance(numeric_level, int):
        logging.getLogger().setLevel(numeric_level)
    
    # Log system info
    ptb_logger.log_system_info()
    
    return ptb_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance. Convenience function."""
    return logging.getLogger(name)

# Context managers for logging
class LoggingContext:
    """Context manager for logging operation start/end."""
    
    def __init__(self, logger: logging.Logger, operation: str, level: int = logging.INFO):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is None:
            return False
            
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.log(self.level, f"Completed {self.operation} in {duration:.3f}s")
        else:
            self.logger.error(f"Failed {self.operation} after {duration:.3f}s: {exc_val}")
        
        # Log performance metric
        perf_logger = logging.getLogger('performance')
        status = "success" if exc_type is None else "failure"
        perf_logger.info(f"OPERATION: {self.operation} duration={duration:.3f}s status={status}")

class TeamOperationLogger:
    """Specialized logger for team operations."""
    
    def __init__(self, team_name: str = "Unknown"):
        self.team_name = team_name
        self.logger = get_logger(f'ptb.team.{team_name.lower().replace(" ", "_")}')
    
    def log_pokemon_added(self, pokemon_name: str, position: int):
        """Log Pokemon addition."""
        self.logger.info(f"Added {pokemon_name} to position {position} in team {self.team_name}")
    
    def log_pokemon_removed(self, pokemon_name: str, position: int):
        """Log Pokemon removal."""
        self.logger.info(f"Removed {pokemon_name} from position {position} in team {self.team_name}")
    
    def log_team_analysis(self, score: float, issues_count: int):
        """Log team analysis results."""
        self.logger.info(f"Team analysis: score={score}/100 issues={issues_count}")
    
    def log_team_optimization(self, changes_count: int):
        """Log team optimization."""
        self.logger.info(f"Team optimization completed: {changes_count} changes suggested")
    
    def log_battle_result(self, opponent: str, won: bool, turns: int):
        """Log battle results."""
        result = "won" if won else "lost"
        self.logger.info(f"Battle vs {opponent}: {result} in {turns} turns")

# Initialize default logger
default_ptb_logger = None

def initialize_application_logging(log_level: str = "INFO") -> PTBLogger:
    """Initialize logging for the entire application."""
    global default_ptb_logger
    default_ptb_logger = setup_logging(log_level)
    return default_ptb_logger

def get_application_logger() -> Optional[PTBLogger]:
    """Get the application logger instance."""
    return default_ptb_logger