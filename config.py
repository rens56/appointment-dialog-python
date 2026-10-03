"""
Configuration Module
Leest en beheert de applicatie-configuratie uit config.ini
"""

import configparser
from pathlib import Path


class Config:
    """Configuratie-manager voor de applicatie"""

    def __init__(self, config_file="config.ini"):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        
        # Controleer of het bestand bestaat
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuratiebestand niet gevonden: {self.config_file}")
        
        # Lees het configuratiebestand
        self.config.read(self.config_file, encoding='utf-8')

    # Application settings
    def get_app_name(self):
        return self.config.get('Application', 'app_name', fallback='Afsprakenbeheer')

    def get_app_version(self):
        return self.config.get('Application', 'app_version', fallback='1.0.0')

    # Website settings
    def get_website_options(self):
        """Geef alle websites met naam en URL terug"""
        websites = []
        website_keys = [key for key in self.config['Websites'] if key.endswith('_name')]
        
        for name_key in website_keys:
            website_id = name_key.replace('_name', '')
            name = self.config.get('Websites', name_key)
            url = self.config.get('Websites', f'{website_id}_url', fallback='')
            websites.append((name, website_id))
        
        return websites

    def get_website_url(self, website_id):
        """Geef de URL van een website terug"""
        return self.config.get('Websites', f'{website_id}_url', fallback='')

    def get_website_name(self, website_id):
        """Geef de naam van een website terug"""
        return self.config.get('Websites', f'{website_id}_name', fallback=website_id)

    def is_test_website(self, website_id):
        """Controleer of het een test-website is"""
        return website_id == 'test_website'

    # Logging settings
    def get_log_directory(self):
        return self.config.get('Logging', 'log_directory', fallback='logs')

    def get_log_name(self):
        return self.config.get('Logging', 'log_name', fallback='appointments')

    # UI settings
    def get_window_title(self):
        return self.config.get('UI', 'window_title', fallback='Afsprakenbeheer')

    def get_window_width_percent(self):
        return float(self.config.get('UI', 'window_width_percent', fallback='0.9'))

    def get_window_height_percent(self):
        return float(self.config.get('UI', 'window_height_percent', fallback='0.9'))

    def get_default_time(self):
        return self.config.get('UI', 'default_time', fallback='09:00')

    # Import/Export settings
    def get_csv_encoding(self):
        return self.config.get('Import_Export', 'csv_encoding', fallback='utf-8')

    def get_default_export_format(self):
        return self.config.get('Import_Export', 'default_export_format', fallback='afspraken_%Y%m%d_%H%M%S')
