"""
Logging Module
Centraliseerde logging met configuratie-ondersteuning
"""

import logging
from datetime import datetime
from pathlib import Path


class Logger:
    """Centraliseerde logger voor de applicatie"""

    def __init__(self, config=None):
        self.config = config
        
        # Bepaal logbestand-locatie
        if config:
            log_dir_name = config.get_log_directory()
            log_name = config.get_log_name()
        else:
            log_dir_name = "logs"
            log_name = "appointments"
        
        # Setup logging directory
        self.log_dir = Path(log_dir_name)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"{log_name}_{datetime.now().strftime('%Y%m%d')}.log"

        # Remove all existing handlers
        logging.root.handlers = []

        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def info(self, message):
        """Log een informatiebericht"""
        self.logger.info(message)

    def error(self, message):
        """Log een foutbericht"""
        self.logger.error(message)

    def warning(self, message):
        """Log een waarschuwingsbericht"""
        self.logger.warning(message)

    def debug(self, message):
        """Log een debug bericht"""
        self.logger.debug(message)

    def get_log_file(self):
        """Geef het pad van het logbestand terug"""
        return self.log_file
