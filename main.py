"""
Hoofdapplicatie - Entry Point
Importeert en start de appointment dialog met website processing en configuratie.
"""

import tkinter as tk

from appointment_dialog import AppointmentDialog
from website_processing import WebsiteProcessor
from logger import Logger
from config import Config


def main():
    """Start de applicatie"""
    try:
        # Load configuration
        config = Config(config_file="config.ini")
        
        # Initialize centralized logger
        logger = Logger(config=config)
        
        # Initialize window
        root = tk.Tk()
        
        # Initialize modules
        website_processor = WebsiteProcessor(config=config)
        
        # Start application with shared resources
        app = AppointmentDialog(root, logger, config, website_processor)
        root.mainloop()
        
    except FileNotFoundError as e:
        print(f"Fout: {e}")
        print("Zorg ervoor dat config.ini in dezelfde map staat als main.py")


if __name__ == "__main__":
    main()
