"""
Appointment Dialog Screen
- Left column: Select website/test website + Login
- Right column: Make appointments with repeat options, select days
- Bottom: Import/Export (CSV)
- All actions are logged and displayed at bottom of screen
- Screen fits within screen bounds
"""

import csv
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from website_processing import WebsiteProcessor


class AppointmentDialog:
    def __init__(self, root, logger, config, website_processor=None):
        self.root = root
        self.logger = logger
        self.config = config
        self.website_processor = website_processor or WebsiteProcessor(config, logger)
        self.root.title(config.get_window_title())
        self.root.geometry("1200x700")
        
        # Get screen dimensions
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window to fit screen (using config percentages)
        window_width = int(screen_width * config.get_window_width_percent())
        window_height = int(screen_height * config.get_window_height_percent())
        self.root.geometry(f"{window_width}x{window_height}")
        
        self.logger.info("Applicatie gestart")
        
        # Store appointments
        self.appointments = []
        self.selected_appointment_index = None
        
        # Create main layout
        self.create_ui()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """Handle window closing"""
        self.website_processor.close_driver()
        self.root.destroy()
        
    def create_ui(self):
        """Create the main UI with two columns and log area"""
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section with two columns
        columns_frame = ttk.Frame(main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # LEFT COLUMN: Website Selection and Login
        self.create_left_column(columns_frame)
        
        # RIGHT COLUMN: Appointment Creation
        self.create_right_column(columns_frame)
        
        # MIDDLE SECTION: Action Buttons
        self.create_button_section(main_frame)
        
        # BOTTOM SECTION: Log Display
        self.create_log_section(main_frame)
        
    def create_left_column(self, parent):
        """Left column: Website selection and login"""
        
        left_frame = ttk.LabelFrame(parent, text="Website Selectie & Inloggen", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Website selection
        ttk.Label(left_frame, text="Selecteer Website:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        self.website_var = tk.StringVar(value="website1")
        
        for label, value in self.website_processor.get_options():
            rb = ttk.Radiobutton(
                left_frame,
                text=label,
                variable=self.website_var,
                value=value,
                command=lambda val=value, lbl=label: self.on_website_selected(val, lbl)
            )
            rb.pack(anchor=tk.W, pady=3)
        
        # Separator
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Display current selection
        ttk.Label(left_frame, text="Huidige selectie:", font=("Arial", 9)).pack(anchor=tk.W, pady=5)
        self.selection_label = ttk.Label(left_frame, text="Website 1", foreground="blue")
        self.selection_label.pack(anchor=tk.W, pady=5)
        
        # Website URL display
        ttk.Label(left_frame, text="Website URL:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 3))
        self.url_label = ttk.Label(left_frame, text="", foreground="darkblue", font=("Arial", 8))
        self.url_label.pack(anchor=tk.W, pady=5)
        
        # Login section
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Inloggen:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        # Username field
        ttk.Label(left_frame, text="Gebruikersnaam:", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 2))
        self.username_entry = ttk.Entry(left_frame, width=30)
        self.username_entry.pack(anchor=tk.W, pady=3, fill=tk.X, padx=5)
        
        # Password field
        ttk.Label(left_frame, text="Wachtwoord:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 2))
        self.password_entry = ttk.Entry(left_frame, width=30, show="*")
        self.password_entry.pack(anchor=tk.W, pady=3, fill=tk.X, padx=5)
        
        # Login button
        self.login_button = ttk.Button(
            left_frame,
            text="🔐 Inloggen",
            command=self.login_to_website
        )
        self.login_button.pack(fill=tk.X, pady=10, padx=5)
        
        # Logout button
        self.logout_button = ttk.Button(
            left_frame,
            text="🔓 Afmelden",
            command=self.logout_from_website,
            state=tk.DISABLED
        )
        self.logout_button.pack(fill=tk.X, pady=5, padx=5)
        
        # Status label
        ttk.Label(left_frame, text="Status:", font=("Arial", 9)).pack(anchor=tk.W, pady=(10, 2))
        self.login_status = ttk.Label(left_frame, text="Niet ingelogd", foreground="red", font=("Arial", 9, "bold"))
        self.login_status.pack(anchor=tk.W, pady=5)
        
        # WARNING PANEL for test website (initially hidden)
        self.warning_frame = ttk.LabelFrame(left_frame, text="⚠️ WAARSCHUWING", padding=10, relief=tk.RAISED)
        
        warning_text = ttk.Label(
            self.warning_frame,
            text="U heeft de TEST WEBSITE geselecteerd!\n\nDit is een testomgeving.\nGebruik dit alleen voor testen.\n\nVeranderen naar een ander website\nom deze waarschuwing weg te halen.",
            font=("Arial", 9),
            foreground="darkred",
            justify=tk.LEFT
        )
        warning_text.pack(anchor=tk.W, pady=5)
        
    def on_website_selected(self, value, label):
        """Handle website selection with persistent warning for test website"""
        self.selection_label.config(text=label)
        
        # Display URL
        url = self.website_processor.get_url(value)
        self.url_label.config(text=url if url else "Geen URL geconfigureerd")
        
        # Reset login status when switching websites
        self.login_status.config(text="Niet ingelogd", foreground="red")
        self.login_button.config(state=tk.NORMAL)
        self.logout_button.config(state=tk.DISABLED)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        
        if self.website_processor.is_test_website(value):
            # Show warning frame
            self.warning_frame.pack(fill=tk.X, pady=10)
            self.log_action(f"⚠️ TEST WEBSITE geselecteerd - WAARSCHUWING ACTIEF!")
        else:
            # Hide warning frame
            self.warning_frame.pack_forget()
            self.log_action(f"✅ Website geselecteerd: {label}")
    
    def login_to_website(self):
        """Login to the selected website"""
        website_id = self.website_var.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Waarschuwing", "Vul gebruikersnaam en wachtwoord in!")
            self.log_action("❌ Login mislukt: lege velden")
            return
        
        # Show processing message
        self.login_status.config(text="Bezig met inloggen...", foreground="orange")
        self.root.update()
        
        # Attempt login
        self.log_action(f"🔐 Poging inloggen op {self.website_processor.get_label(website_id)}...")
        success = self.website_processor.login(website_id, username, password)
        
        if success:
            self.login_status.config(text="Ingelogd ✓", foreground="green")
            self.login_button.config(state=tk.DISABLED)
            self.logout_button.config(state=tk.NORMAL)
            self.log_action(f"✅ Succesvol ingelogd op {self.website_processor.get_label(website_id)}")
        else:
            self.login_status.config(text="Niet ingelogd", foreground="red")
            self.log_action(f"❌ Inloggen mislukt op {self.website_processor.get_label(website_id)}")
    
    def logout_from_website(self):
        """Logout from the website"""
        self.website_processor.close_driver()
        self.login_status.config(text="Niet ingelogd", foreground="red")
        self.login_button.config(state=tk.NORMAL)
        self.logout_button.config(state=tk.DISABLED)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.log_action("🔓 Afgelogd")
        
    def create_right_column(self, parent):
        """Right column: Appointment creation with repeat options"""
        
        right_frame = ttk.LabelFrame(parent, text="Afspraak Maken", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Time selection
        ttk.Label(right_frame, text="Tijd:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        time_frame = ttk.Frame(right_frame)
        time_frame.pack(anchor=tk.W, pady=3)
        
        ttk.Label(time_frame, text="Uur:").pack(side=tk.LEFT, padx=5)
        
        # Get default time from config
        default_time = self.config.get_default_time()
        default_hour = default_time.split(':')[0] if ':' in default_time else "09"
        default_minute = default_time.split(':')[1] if ':' in default_time else "00"
        
        self.hour_var = tk.StringVar(value=default_hour)
        hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, width=3, textvariable=self.hour_var, format="%02.0f")
        hour_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(time_frame, text="Minuut:").pack(side=tk.LEFT, padx=5)
        self.minute_var = tk.StringVar(value=default_minute)
        minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, width=3, textvariable=self.minute_var, format="%02.0f")
        minute_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Description
        ttk.Label(right_frame, text="Beschrijving:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 3))
        self.description_entry = ttk.Entry(right_frame, width=40)
        self.description_entry.pack(anchor=tk.W, pady=3)
        
        # Repeat options
        ttk.Label(right_frame, text="Herhaling:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 3))
        
        self.repeat_var = tk.StringVar(value="geen")
        repeat_options = [
            ("Geen", "geen"),
            ("Dagelijks", "daily"),
            ("Wekelijks", "weekly"),
            ("Maandelijks", "monthly"),
        ]
        
        for label, value in repeat_options:
            rb = ttk.Radiobutton(right_frame, text=label, variable=self.repeat_var, value=value)
            rb.pack(anchor=tk.W, pady=2)
        
        # Days of week selection
        ttk.Label(right_frame, text="Dagen (voor wekelijkse herhaling):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 3))
        
        self.days_vars = {}
        days = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
        days_frame = ttk.Frame(right_frame)
        days_frame.pack(anchor=tk.W, pady=3)
        
        for day in days:
            var = tk.BooleanVar()
            self.days_vars[day] = var
            cb = ttk.Checkbutton(days_frame, text=day, variable=var)
            cb.pack(side=tk.LEFT, padx=2)
        
        # Number of repeats
        ttk.Label(right_frame, text="Aantal herhalingen:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 3))
        self.repeat_count_var = tk.StringVar(value="1")
        repeat_count_spinbox = ttk.Spinbox(right_frame, from_=1, to=52, width=5, textvariable=self.repeat_count_var)
        repeat_count_spinbox.pack(anchor=tk.W, pady=3)
        
        # Add appointment button
        self.add_button = ttk.Button(
            right_frame,
            text="➕ Afspraak Toevoegen",
            command=self.add_appointment
        )
        self.add_button.pack(fill=tk.X, pady=10)
        
        # List of appointments
        ttk.Label(right_frame, text="Geplande Afspraken:", font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(10, 3))
        
        self.appointments_listbox = tk.Listbox(right_frame, height=6)
        self.appointments_listbox.pack(fill=tk.BOTH, expand=True, pady=3)
        self.appointments_listbox.bind('<<ListboxSelect>>', self.on_appointment_selected)
        
        # Button frame for actions
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=3)
        
        # Delete appointment button
        self.delete_button = ttk.Button(
            button_frame,
            text="🗑️ Verwijderen",
            command=self.delete_appointment
        )
        self.delete_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Update appointment button
        self.update_button = ttk.Button(
            button_frame,
            text="💾 Wijzigingen Opslaan",
            command=self.update_appointment,
            state=tk.DISABLED
        )
        self.update_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Clear form button
        self.clear_button = ttk.Button(
            button_frame,
            text="🔄 Formulier Wissen",
            command=self.clear_form,
            state=tk.DISABLED
        )
        self.clear_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
    def create_button_section(self, parent):
        """Create import/export buttons"""
        
        button_frame = ttk.LabelFrame(parent, text="Import/Export", padding=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        col_frame = ttk.Frame(button_frame)
        col_frame.pack(fill=tk.X)
        
        ttk.Button(
            col_frame,
            text="📥 Importeren (CSV)",
            command=self.import_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            col_frame,
            text="📤 Exporteren (CSV)",
            command=self.export_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            col_frame,
            text="🔄 Vernieuwen Log",
            command=self.refresh_log
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            col_frame,
            text="❌ Alles Wissen",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=5)
        
    def create_log_section(self, parent):
        """Create log display at bottom"""
        
        log_frame = ttk.LabelFrame(parent, text="Activiteitenlog (realtime)", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        self.log_text = tk.Text(log_frame, height=8, yscrollcommand=scrollbar.set, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Initial log message
        self.log_action(f"Applicatie gestart. Logbestand: {self.logger.get_log_file()}")
        
    def log_action(self, message):
        """Log action to both file and UI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # Log to file
        self.logger.info(message)
        
        # Add to text widget
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)  # Auto-scroll to bottom
        self.root.update()
    
    def on_appointment_selected(self, event):
        """Handle appointment selection from listbox"""
        selection = self.appointments_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_appointment_index = index
            apt = self.appointments[index]
            
            # Load appointment data into form
            self.website_var.set(apt["website"])
            self.on_website_selected(apt["website"], self.website_processor.get_label(apt["website"]))
            
            time_parts = apt["time"].split(":")
            self.hour_var.set(time_parts[0])
            self.minute_var.set(time_parts[1])
            
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, apt["description"])
            
            self.repeat_var.set(apt["repeat"])
            self.repeat_count_var.set(str(apt["repeat_count"]))
            
            # Set days
            for day in self.days_vars:
                self.days_vars[day].set(False)
            
            if apt["days"] != "Alle dagen":
                days_list = [d.strip() for d in apt["days"].split(",")]
                for day in days_list:
                    if day in self.days_vars:
                        self.days_vars[day].set(True)
            
            # Enable update buttons
            self.update_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
            self.add_button.config(text="📝 Nieuwe Afspraak", state=tk.NORMAL)
            
            self.log_action(f"📋 Afspraak geselecteerd: {apt['description']}")
    
    def clear_form(self):
        """Clear the form and deselect any selected appointment"""
        self.selected_appointment_index = None
        self.website_var.set("website1")
        self.on_website_selected("website1", "Website 1")
        
        default_time = self.config.get_default_time()
        default_hour = default_time.split(':')[0] if ':' in default_time else "09"
        default_minute = default_time.split(':')[1] if ':' in default_time else "00"
        
        self.hour_var.set(default_hour)
        self.minute_var.set(default_minute)
        self.description_entry.delete(0, tk.END)
        self.repeat_var.set("geen")
        self.repeat_count_var.set("1")
        
        for day in self.days_vars:
            self.days_vars[day].set(False)
        
        self.appointments_listbox.selection_clear(0, tk.END)
        self.update_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.add_button.config(text="➕ Afspraak Toevoegen")
        
        self.log_action("📝 Formulier geleegd")
    
    def add_appointment(self):
        """Add a new appointment"""
        try:
            website = self.website_var.get()
            time_str = f"{self.hour_var.get()}:{self.minute_var.get()}"
            description = self.description_entry.get()
            repeat_type = self.repeat_var.get()
            repeat_count = int(self.repeat_count_var.get())
            
            if not description:
                messagebox.showwarning("Waarschuwing", "Vul een beschrijving in!")
                self.log_action("❌ Afspraak niet toegevoegd: geen beschrijving")
                return
            
            selected_days = [day for day, var in self.days_vars.items() if var.get()]
            
            appointment = {
                "website": website,
                "time": time_str,
                "description": description,
                "repeat": repeat_type,
                "repeat_count": repeat_count,
                "days": ", ".join(selected_days) if selected_days else "Alle dagen",
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.appointments.append(appointment)
            self.update_appointments_list()
            self.clear_form()
            
            self.log_action(f"✅ Afspraak toegevoegd: {description} om {time_str} op {website}")
            
        except Exception as e:
            self.log_action(f"❌ Fout bij toevoegen: {str(e)}")
            messagebox.showerror("Fout", f"Fout bij toevoegen: {str(e)}")
    
    def update_appointment(self):
        """Update the selected appointment"""
        try:
            if self.selected_appointment_index is None:
                messagebox.showwarning("Waarschuwing", "Selecteer een afspraak om te wijzigen!")
                self.log_action("❌ Geen afspraak geselecteerd voor wijziging")
                return
            
            website = self.website_var.get()
            time_str = f"{self.hour_var.get()}:{self.minute_var.get()}"
            description = self.description_entry.get()
            repeat_type = self.repeat_var.get()
            repeat_count = int(self.repeat_count_var.get())
            
            if not description:
                messagebox.showwarning("Waarschuwing", "Vul een beschrijving in!")
                self.log_action("❌ Wijziging niet opgeslagen: geen beschrijving")
                return
            
            selected_days = [day for day, var in self.days_vars.items() if var.get()]
            
            old_apt = self.appointments[self.selected_appointment_index]
            
            self.appointments[self.selected_appointment_index] = {
                "website": website,
                "time": time_str,
                "description": description,
                "repeat": repeat_type,
                "repeat_count": repeat_count,
                "days": ", ".join(selected_days) if selected_days else "Alle dagen",
                "date_added": old_apt["date_added"]
            }
            
            self.update_appointments_list()
            self.clear_form()
            
            self.log_action(f"✏️ Afspraak bijgewerkt: {old_apt['description']} → {description}")
            
        except Exception as e:
            self.log_action(f"❌ Fout bij bijwerken: {str(e)}")
            messagebox.showerror("Fout", f"Fout bij bijwerken: {str(e)}")
            
    def delete_appointment(self):
        """Delete selected appointment"""
        try:
            selection = self.appointments_listbox.curselection()
            if not selection:
                messagebox.showwarning("Waarschuwing", "Selecteer een afspraak om te verwijderen!")
                self.log_action("❌ Geen afspraak geselecteerd voor verwijdering")
                return
            
            index = selection[0]
            deleted = self.appointments.pop(index)
            self.update_appointments_list()
            self.clear_form()
            
            self.log_action(f"🗑️ Afspraak verwijderd: {deleted['description']}")
            
        except Exception as e:
            self.log_action(f"❌ Fout bij verwijderen: {str(e)}")
            messagebox.showerror("Fout", f"Fout bij verwijderen: {str(e)}")
            
    def update_appointments_list(self):
        """Update the listbox with current appointments"""
        self.appointments_listbox.delete(0, tk.END)
        for i, apt in enumerate(self.appointments, 1):
            display_text = f"{i}. {apt['time']} - {apt['description']} ({apt['website']})"
            self.appointments_listbox.insert(tk.END, display_text)
            
    def export_csv(self):
        """Export appointments to CSV file"""
        try:
            if not self.appointments:
                messagebox.showwarning("Waarschuwing", "Geen afspraken om te exporteren!")
                self.log_action("❌ Export mislukt: geen afspraken")
                return
            
            # Get settings from config
            encoding = self.config.get_csv_encoding()
            export_format = self.config.get_default_export_format()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=datetime.now().strftime(export_format + ".csv")
            )
            
            if not file_path:
                self.log_action("❌ Export geannuleerd")
                return
            
            with open(file_path, 'w', newline='', encoding=encoding) as csvfile:
                fieldnames = ["Website", "Tijd", "Beschrijving", "Herhaling", "Aantal", "Dagen", "Datum Toegevoegd"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for apt in self.appointments:
                    writer.writerow({
                        "Website": apt["website"],
                        "Tijd": apt["time"],
                        "Beschrijving": apt["description"],
                        "Herhaling": apt["repeat"],
                        "Aantal": apt["repeat_count"],
                        "Dagen": apt["days"],
                        "Datum Toegevoegd": apt["date_added"]
                    })
            
            self.log_action(f"✅ Geëxporteerd naar: {file_path}")
            messagebox.showinfo("Succes", f"Afspraken geëxporteerd naar:\n{file_path}")
            
        except Exception as e:
            self.log_action(f"❌ Export fout: {str(e)}")
            messagebox.showerror("Fout", f"Fout bij exporteren: {str(e)}")
            
    def import_csv(self):
        """Import appointments from CSV file"""
        try:
            # Get settings from config
            encoding = self.config.get_csv_encoding()
            
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                self.log_action("❌ Import geannuleerd")
                return
            
            imported_count = 0
            imported_appointments = []
            
            with open(file_path, 'r', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    appointment = {
                        "website": row.get("Website", ""),
                        "time": row.get("Tijd", ""),
                        "description": row.get("Beschrijving", ""),
                        "repeat": row.get("Herhaling", "geen"),
                        "repeat_count": int(row.get("Aantal", 1)),
                        "days": row.get("Dagen", "Alle dagen"),
                        "date_added": row.get("Datum Toegevoegd", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                    self.appointments.append(appointment)
                    imported_appointments.append(appointment)
                    imported_count += 1
            
            self.update_appointments_list()
            
            # Log each imported appointment
            self.log_action(f"📥 Import gestart: {file_path}")
            for apt in imported_appointments:
                self.log_action(f"  ✅ Geïmporteerd: {apt['description']} om {apt['time']} op {apt['website']}")
            
            self.log_action(f"✅ Import afgerond: {imported_count} afspraken geïmporteerd")
            messagebox.showinfo("Succes", f"{imported_count} afspraken geïmporteerd!\nZie het log voor details.")
            
        except Exception as e:
            self.log_action(f"❌ Import fout: {str(e)}")
            messagebox.showerror("Fout", f"Fout bij importeren: {str(e)}")
            
    def refresh_log(self):
        """Refresh log display"""
        self.log_action("🔄 Log vernieuwd")
        
    def clear_all(self):
        """Clear all appointments"""
        if not self.appointments:
            messagebox.showinfo("Info", "Geen afspraken om te wissen!")
            self.log_action("❌ Geen afspraken om te wissen")
            return
        
        if messagebox.askyesno("Bevestiging", "Weet je zeker dat je alle afspraken wilt wissen?"):
            self.appointments.clear()
            self.update_appointments_list()
            self.clear_form()
            self.log_action("🗑️ Alle afspraken verwijderd")
        else:
            self.log_action("❌ Wissen geannuleerd")
