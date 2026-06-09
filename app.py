import os
import sys
import re
import json
import threading
import time
import shutil
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import pyrebase

# ───────────────────────────────────────────────────────────────────────
# HARDCODED RELEASE VERSION TRACKER & BRANDING
# ───────────────────────────────────────────────────────────────────────
CURRENT_VERSION = "4.1"
COPYRIGHT_TEXT = "Copyright © 2026 Talha Tools. All rights reserved."

# Configure high-density dark display environment theme properties
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ───────────────────────────────────────────────────────────────────────
# PERMISSION-SAFE LOG CUSHION WORKSPACE ENVIRONMENT
# ───────────────────────────────────────────────────────────────────────
_appdata_workspace = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'TalhaPanicAnalyzer')
os.makedirs(_appdata_workspace, exist_ok=True)
SESSION_FILE = os.path.join(_appdata_workspace, ".session.json")

# ───────────────────────────────────────────────────────────────────────
# LIVE FIREBASE AUTHENTICATION CONFIGURATION PROFILE
# ───────────────────────────────────────────────────────────────────────
config = {
    "apiKey": "AIzaSyDH4VCfQF-IKMbziy4VcG6JTKOttPh3jJw",
    "authDomain": "talha-iphone-panic-analyzer.firebaseapp.com",
    "databaseURL": "https://talha-iphone-panic-analyzer-default-rtdb.firebaseio.com",
    "projectId": "talha-iphone-panic-analyzer",
    "storageBucket": "talha-iphone-panic-analyzer.firebasestorage.app",
    "messagingSenderId": "375157961434",
    "appId": "1:375157961434:web:280a5831dfeebe8f64ebe3"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

def get_hwid():
    """Generates a unique hardware fingerprint from the local Windows motherboard."""
    try:
        cmd = "wmic csproduct get uuid"
        uuid = subprocess.check_output(cmd, shell=True, text=True).split("\n")[1].strip()
        return uuid
    except Exception:
        return os.environ.get('COMPUTERNAME', 'UNKNOWN_HARDWARE_NODE')


# ───────────────────────────────────────────────────────────────────────
# MASTER MULTI-GENERATION HARDWARE REGISTRY
# ───────────────────────────────────────────────────────────────────────
BITMASK_REGISTRY = {
    "32": "Charging Circuit / USB Controller Interrupted [Tristar/Hydra PMIC Error]",
    "64": "Gas Gauge Data Line Connection Drop [Battery Communication Error]",
    "65": "Battery System Identification Circuit Fault [Fuel Gauge Transceiver Disconnection]",
    "161": "Battery NTC Thermistor Failure [TG0B Core Sensor Array Fault]",
    "1024": "Main Logic Board Interposer Sandwich Separation [Mini Series Structural Defect]",
    "2048": "Lower Charging Port Dock Flex Assembly [PRS0 Barometric Sensor / Mic1 Fault Line]",
    "4096": "Front Top Screen Flex Assembly [TH0F Proximity Array / Ambient Light Sensor Interruption]",
    "8192": "Audio Codec Subsystem Error [Speaker/Microphone Serial Bus Line Freeze]",
    "16384": "Main Battery Pack Data Interface Line [TG0B Gas Gauge / I2C Bus Protocol Freeze]",
    "32768": "Rear Camera Array Sensor Disruption [Image Stabilizer Actuator Fault]",
    "65536": "Power / Volume Control Strip Array [Mic2 Thermal Strobe Interruption]",
    "131072": "Baseband Processor / Cellular Modem Hardware Communication Failure",
    "262144": "Wi-Fi & Bluetooth Module Subsystem Crash [VDD_MAIN Power Rail Drop]",
    "524288": "Front Screen Ambient Light Sensor (ALS) Matrix Interruption",
    "1048576": "Lower Charging Port Dock Flex Assembly [Secondary Validation Layer Routing]",
    "2097152": "Front Screen Proximity Sensor / FaceID Dot Projector Alignment Loop",
    "4194304": "Wireless Charging Coil Flex / Back Glass MagSafe Inductor Module Assembly",
    "6144": "Dual Failure: Lower Charging Port Dock Flex AND Front Proximity Screen Flex Cables",
    "18432": "Dual Failure: Lower Charging Port Dock Flex AND Main Battery Pack Data Interface Line",
    "20480": "Dual Failure: Front Top Screen Flex AND Main Battery Pack Data Interface Line",
    "6291456": "Dual Failure: Front Screen Proximity Flex AND Wireless Charging Coil Flex Cables",

    "0x20": "Charging Circuit / USB Controller Interrupted [Tristar/Hydra PMIC Error]",
    "0x40": "Gas Gauge Data Line Connection Drop [Battery Communication Error]",
    "0x41": "Battery System Identification Circuit Fault [Fuel Gauge Transceiver Disconnection]",
    "0xA1": "Battery NTC Thermistor Failure [TG0B Core Sensor Array Fault]",
    "0x400": "Main Logic Board Interposer Sandwich Separation [Mini Series Structural Defect]",
    "0x800": "Lower Charging Port Dock Flex Assembly [PRS0 Barometric Sensor / Mic1 Fault Line]",
    "0x1000": "Front Top Screen Flex Assembly [TH0F Proximity Array / Ambient Light Sensor Interruption]",
    "0x2000": "Audio Codec Subsystem Error [Speaker/Microphone Serial Bus Line Freeze]",
    "0x4000": "Main Battery Pack Data Interface Line [TG0B Gas Gauge / I2C Bus Protocol Freeze]",
    "0x8000": "Rear Camera Array Sensor Disruption [Image Stabilizer Actuator Fault]",
    "0x10000": "Power / Volume Control Strip Array [Mic2 Thermal Strobe Interruption]",
    "0x20000": "Baseband Processor / Cellular Modem Hardware Communication Failure",
    "0x40000": "Wi-Fi & Bluetooth Module Subsystem Crash [VDD_MAIN Power Rail Drop]",
    "0x80000": "Front Screen Ambient Light Sensor (ALS) Matrix Interruption",
    "0x100000": "Lower Charging Port Dock Flex Assembly [Secondary Validation Layer Routing]",
    "0x200000": "Front Screen Proximity Sensor / FaceID Dot Projector Alignment Loop",
    "0x400000": "Wireless Charging Coil Flex / Back Glass MagSafe Inductor Module Assembly",
    "0x1800": "Dual Failure: Lower Charging Port Dock Flex AND Front Proximity Screen Flex Cables",
    "0x4800": "Dual Failure: Lower Charging Port Dock Flex AND Main Battery Pack Data Interface Line",
    "0x5000": "Dual Failure: Front Top Screen Flex AND Main Battery Pack Data Interface Line",
    "0x600000": "Dual Failure: Front Screen Proximity Flex AND Wireless Charging Coil Flex Cables",

    "131072": "Main Logic Board Structural Separation [Double-Decker Interposer Solder Joint Fracture]",
    "262144": "Lower Charging Port Dock Lightning Flex Ribbon Cable Assembly",
    "786432": "Dual Failure: Front Screen Proximity Flex AND Lower Charging Port Dock Flex Cables",
    "327680": "Dual Failure: Power Button Flex AND Lower Charging Port Dock Flex Cables",
    "589824": "Dual Failure: Power Button Flex AND Front Screen Proximity Flex Cables",
    "655360": "Dual Failure: Main Logic Board Sandwich Separation AND Front Screen Proximity Flex",
    "1179648": "Triple Failure: Lower Charging Port Dock + Power Button + Front Proximity Flex Cables",

    "0x400": "Inertial Gyroscope Sensor Failure [U7300 Accelerometer Circuit Disruption]",
    "0x10000": "Power Button / Volume Control Strip / Rear Strobe Flash Flex Cable Assembly",
    "0x20000": "Main Logic Board Structural Separation [Double-Decker Interposer Solder Joint Fracture]",
    "0x40000": "Lower Charging Port Dock Lightning Flex Ribbon Cable Assembly",
    "0x80000": "Front Screen Dynamic Island Ambient Light Sensor Array Flex Cable",
    "0xC0000": "Dual Failure: Front Screen Proximity Flex AND Lower Charging Port Dock Flex Cables",
    "0x50000": "Dual Failure: Power Button Flex AND Lower Charging Port Dock Flex Cables",
    "0x90000": "Dual Failure: Power Button Flex AND Front Screen Proximity Flex Cables",
    "0xA0000": "Dual Failure: Main Logic Board Sandwich Separation AND Front Screen Proximity Flex",
    "0x1C0000": "Triple Failure: Lower Charging Port Dock + Power Button + Front Proximity Flex Cables",

    "0x80000": "Lower USB-C Charging Port Dock Flex Assembly",
    "0x100000": "Front Screen Top Proximity Module Loop Line",
    "0x200000": "Wireless Charging Inductive Loop / Rear Housing Matte Assembly Line",
    "0x280000": "Dual Failure: Lower USB-C Charging Port Dock AND Wireless Charging Coil Flex Cables",
    "0x380000": "Triple Failure: Lower USB-C Charging Port Dock + Wireless Coil + Front Proximity Flex",

    "0x20000": "Main Logic Board Core Interposer Layer Drop [A17 Pro Sandwich Crack]",
    "0x80000": "Rear LiDAR Sensor / Auxiliary TrueDepth Structural Array Interruption",
    "0x100000": "Front Dynamic Island Proximity Array & Infrared Camera Array Assembly",
    "0x200000": "Front FaceID Camera System / Ambient Light Sensor Array Line",
    "0x300000": "Lower USB-C High-Speed Main Charging Port Dock Flex Assembly",
    "0x400000": "Wireless Charging Core Matrix Inductor / Back Glass Thermal Sense Loop",

    "OUTBOX3 not ready": "AOP to Power Management IC (PMIC) Communication Timeout [Check Main Logic Rails]",
    "OUTBOX0 not ready": "AOP to Audio Codec Core Bus Communication Link Failure",
    "OUTBOX1 not ready": "AOP to Baseband Processor/Modem Shared Communication Handshake Timeout",
    "INBOX3 not ready": "Power Management IC (PMIC) to AOP Return Interrupt Failure",
    "SMC BSC failure": "Logic Board Interposer Sandwich Fracture [SMC to Baseband Link Severed]",

    "watchdog timeout: no successful checkins from thermalmonitord": "Charging Port Flex / Battery I2C Data Line Disruption [Device Reset Every 180s]",
    "watchdog timeout: no successful checkins from wifid": "Wi-Fi or Bluetooth IC Module Hardware Hang / Power Rail VDD_MAIN Short",
    "watchdog timeout: no successful checkins from ans": "NAND Storage Subsystem Error [Apple NVMe Storage Driver Protocol Freeze]",
    "watchdog timeout: no successful checkins from backboardd": "Touch Controller / Display Panel Communication Interruption",

    "sensor name: TG0B": "Battery Proximity Thermistor Sensor Fault [Check Center Battery Pins]",
    "sensor name: TG0V": "Battery Main Power Rail Over-Temperature Defect",
    "sensor name: TH0F": "Front Proximity Sensor / Ear Speaker Assembly Sensor Array Fault"
}

# ───────────────────────────────────────────────────────────────────────
# REMOTE UPDATE INTERCEPTOR SYSTEM
# ───────────────────────────────────────────────────────────────────────
def check_for_mandatory_update(firebase_db, base_window):
    try:
        latest_version = firebase_db.child("latest_version").get().val()
        download_url = firebase_db.child("download_url").get().val()

        if latest_version and float(CURRENT_VERSION) < float(latest_version):
            base_window.withdraw()

            alert = ctk.CTkToplevel(base_window)
            alert.title("Critical Update Required")
            alert.geometry("480x250")
            alert.resizable(False, False)
            alert.attributes("-topmost", True)

            alert.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))

            ctk.CTkLabel(alert, text="⚠️ OUTDATED VERSION DETECTED", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FF4444").pack(pady=(25, 10))
            ctk.CTkLabel(alert, text=f"You are running v{CURRENT_VERSION}.\nVersion {latest_version} is now available with critical patches.\n\nThis build has been deprecated and locked.", justify="center", font=ctk.CTkFont(size=13)).pack(pady=10)

            def trigger_download_and_exit():
                webbrowser.open(download_url)
                sys.exit(0)

            btn = ctk.CTkButton(alert, text=f"Download Update (v{latest_version})", fg_color="#1f538d", hover_color="#14375e", height=40, font=ctk.CTkFont(weight="bold"), command=trigger_download_and_exit)
            btn.pack(pady=15)

    except Exception:
        pass


# ───────────────────────────────────────────────────────────────────────
# SECURITY LOGIN & REGISTRATION INTERFACE
# ───────────────────────────────────────────────────────────────────────
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Talha Panic Analyzer v{CURRENT_VERSION}")
        self.geometry("450x550")
        self.resizable(False, False)
        self.configure(fg_color="#0B0E14")

        try:
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.iconbitmap(os.path.join(base_dir, "logo.ico"))
        except Exception:
            pass

        lbl_title = ctk.CTkLabel(self, text=f"Talha Panic Analyzer v{CURRENT_VERSION}", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00D2FF")
        lbl_title.pack(pady=(25, 15))

        self.tab_view = ctk.CTkTabview(self, width=400, height=420, fg_color="#111622", segmented_button_selected_color="#00D2FF", segmented_button_selected_hover_color="#40C4FF", segmented_button_unselected_hover_color="#1B2234")
        self.tab_view.pack(padx=20, pady=5)

        self.tab_view.add("Sign In")
        self.tab_view.add("Register")

        self.setup_login_tab()
        self.setup_register_tab()

        # ⚖️ ADDED COPYRIGHT WATERMARK TO LOGIN SCREEN
        lbl_copyright = ctk.CTkLabel(self, text=COPYRIGHT_TEXT, font=ctk.CTkFont(size=10), text_color="#64748B")
        lbl_copyright.pack(side=tk.BOTTOM, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.exit_application_completely)
        self.check_saved_session_cache()

    def setup_login_tab(self):
        tab = self.tab_view.tab("Sign In")

        ctk.CTkLabel(tab, text="Email", font=ctk.CTkFont(size=13), text_color="#E2E8F0").pack(anchor="w", padx=25, pady=(20, 2))
        self.login_email = ctk.CTkEntry(tab, width=310, fg_color="#0B0E14", border_color="#1B2234", text_color="#FFFFFF")
        self.login_email.pack(padx=25, pady=(0, 10))

        ctk.CTkLabel(tab, text="Password", font=ctk.CTkFont(size=13), text_color="#E2E8F0").pack(anchor="w", padx=25, pady=(10, 2))
        self.login_pass = ctk.CTkEntry(tab, width=310, show="*", fg_color="#0B0E14", border_color="#1B2234", text_color="#FFFFFF")
        self.login_pass.pack(padx=25, pady=(0, 15))

        self.login_email.bind("<Return>", lambda e: self.handle_login_action())
        self.login_pass.bind("<Return>", lambda e: self.handle_login_action())

        self.remember_var = ctk.StringVar(value="off")
        self.chk_remember = ctk.CTkCheckBox(tab, text="Remember Me", variable=self.remember_var, onvalue="on", offvalue="off", font=ctk.CTkFont(size=12), text_color="#A0AEC0", checkbox_width=18, checkbox_height=18)
        self.chk_remember.pack(anchor="w", padx=25, pady=5)

        btn_login = ctk.CTkButton(tab, text="Login", width=220, height=40, corner_radius=20, fg_color="#00D2FF", text_color="#000000", font=ctk.CTkFont(size=13, weight="bold"), hover_color="#40C4FF", command=lambda: self.handle_login_action())
        btn_login.pack(pady=20)

    def setup_register_tab(self):
        tab = self.tab_view.tab("Register")

        ctk.CTkLabel(tab, text="Full Name", font=ctk.CTkFont(size=12), text_color="#E2E8F0").pack(anchor="w", padx=25, pady=(15, 2))
        self.reg_name = ctk.CTkEntry(tab, width=310, fg_color="#0B0E14", border_color="#1B2234")
        self.reg_name.pack(padx=25, pady=(0, 6))

        ctk.CTkLabel(tab, text="Email", font=ctk.CTkFont(size=12), text_color="#E2E8F0").pack(anchor="w", padx=25, pady=(6, 2))
        self.reg_email = ctk.CTkEntry(tab, width=310, fg_color="#0B0E14", border_color="#1B2234")
        self.reg_email.pack(padx=25, pady=(0, 6))

        ctk.CTkLabel(tab, text="Password", font=ctk.CTkFont(size=12), text_color="#E2E8F0").pack(anchor="w", padx=25, pady=(6, 2))
        self.reg_pass = ctk.CTkEntry(tab, width=310, show="*", fg_color="#0B0E14", border_color="#1B2234")
        self.reg_pass.pack(padx=25, pady=(0, 25))

        btn_reg = ctk.CTkButton(tab, text="Register", width=220, height=40, corner_radius=20, fg_color="#00E676", text_color="#000000", font=ctk.CTkFont(size=13, weight="bold"), hover_color="#66FFA6", command=lambda: self.handle_registration_action())
        btn_reg.pack(pady=10)

    def check_saved_session_cache(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                email = data.get("email")
                password = data.get("password")
                if email and password:
                    self.login_email.delete(0, tk.END)
                    self.login_email.insert(0, email)
                    self.login_pass.delete(0, tk.END)
                    self.login_pass.insert(0, password)
                    self.remember_var.set("on")
                    self.chk_remember.select()
            except Exception:
                pass

    def handle_login_action(self):
        email = self.login_email.get().strip()
        password = self.login_pass.get().strip()
        self.execute_authentication_pipeline(email, password)

    def execute_authentication_pipeline(self, email, password):
        if not email or not password:
            messagebox.showerror("Input Error", "Please fill in all input fields completely.")
            return

        try:
            login = auth.sign_in_with_email_and_password(email, password)
            uid = login['localId']
            account_info = auth.get_account_info(login['idToken'])
            is_verified = account_info['users'][0]['emailVerified']

            if not is_verified:
                messagebox.showerror("Access Denied", "Access Denied: Please verify your email via the sent link before logging in.")
                return

            user_profile = db.child("Users").child(uid).get().val()
            if not user_profile:
                messagebox.showerror("Configuration Error", "Profile configuration error.")
                return

            if user_profile.get("status") == "Blocked":
                messagebox.showerror("Suspended Account", "🚫 ACCOUNT SUSPENDED: Your license has been permanently blocked.")
                return

            current_hwid = get_hwid()
            if user_profile.get("hwid") != current_hwid:
                messagebox.showerror("Hardware Lockout", "❌ HARDWARE MISMATCH: This software license is locked to a different PC.")
                return

            if self.remember_var.get() == "on":
                with open(SESSION_FILE, "w") as f:
                    json.dump({"email": email, "password": password}, f)
            else:
                if os.path.exists(SESSION_FILE):
                    try: os.remove(SESSION_FILE)
                    except Exception: pass

            self.withdraw()
            self.after(100, lambda: self.launch_main_dashboard(user_profile))

        except Exception:
            messagebox.showerror("Authentication Failed", "Login Failed: Invalid credentials or network error.")

    def launch_main_dashboard(self, user_profile):
        app_workspace = MasterWorkspaceContainer(user_profile)
        self.destroy()
        app_workspace.mainloop()

    def handle_registration_action(self):
        fullname = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_pass.get().strip()

        if not fullname or not email or not password:
            messagebox.showerror("Input Error", "Please fill out all registration fields.")
            return

        try:
            user = auth.create_user_with_email_and_password(email, password)
            uid = user['localId']
            auth.send_email_verification(user['idToken'])

            user_data = {
                "fullname": fullname,
                "email": email,
                "hwid": get_hwid(),
                "status": "Active"
            }
            db.child("Users").child(uid).set(user_data)
            messagebox.showinfo("Registration Success", "Registration successful! Please check your email to verify your account.")
            self.tab_view.set("Sign In")

        except Exception as e:
            messagebox.showerror("Registration Error", str(e))

    def exit_application_completely(self):
        self.destroy()
        sys.exit(0)


# ───────────────────────────────────────────────────────────────────────
# MASTER MAIN WORKSPACE CONTAINER
# ───────────────────────────────────────────────────────────────────────
class MasterWorkspaceContainer(ctk.CTk):
    def __init__(self, user_profile):
        super().__init__()

        self.user_profile = user_profile
        self.title(f"Talha Panic Analyzer Pro v{CURRENT_VERSION}")
        self.geometry("1280x780")
        self.minsize(1050, 700)

        self.c_bg_obsidian = "#0B0E14"
        self.c_panel_navy = "#111622"
        self.c_border_slate = "#1B2234"
        self.c_neon_blue = "#00D2FF"
        self.c_neon_green = "#00E676"
        self.c_alert_crimson = "#FF3B30"
        self.c_text_bright = "#E2E8F0"
        self.c_text_muted = "#64748B"

        self.configure(fg_color=self.c_bg_obsidian)

        try:
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.iconbitmap(os.path.join(base_dir, "logo.ico"))
        except Exception:
            pass

        self.connected_device_model = "Unknown Device"
        self.is_device_online = False
        self.imported_log_content = None
        self.selected_file_from_tree = None

        self.assemble_base_interface_layout()
        self.protocol("WM_DELETE_WINDOW", self.close_entire_program)

        self.usb_tracking_active = True
        self.usb_monitor_thread = threading.Thread(target=self.live_usb_handshake_loop, daemon=True)
        self.usb_monitor_thread.start()

    def assemble_base_interface_layout(self):
        header_bar = ctk.CTkFrame(self, fg_color=self.c_panel_navy, height=70, corner_radius=0, border_width=1, border_color=self.c_border_slate)
        header_bar.pack(fill=tk.X, side=tk.TOP)
        header_bar.pack_propagate(False)

        lbl_logo = ctk.CTkLabel(header_bar, text=f"🔷 Talha Panic Analyzer Pro v{CURRENT_VERSION}", font=ctk.CTkFont(family="Arial", size=16, weight="bold"), text_color=self.c_neon_blue)
        lbl_logo.pack(side=tk.LEFT, padx=20)

        self.badge_frame = ctk.CTkFrame(header_bar, fg_color="#1E2235", height=32, corner_radius=6)
        self.badge_frame.pack(side=tk.LEFT, padx=15, pady=19)
        self.badge_text = ctk.CTkLabel(self.badge_frame, text="● NO WORKBENCH TARGET LINKED", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_alert_crimson, padx=12)
        self.badge_text.pack(fill=tk.BOTH, expand=True)

        btn_logout = ctk.CTkButton(header_bar, text="🚪 LOGOUT", fg_color="transparent", border_width=1, border_color=self.c_border_slate, text_color=self.c_text_bright, font=ctk.CTkFont(size=11), hover_color="#FF3B30", height=35, command=self.purge_session_logout_action)
        btn_logout.pack(side=tk.RIGHT, padx=20)

        self.main_body_hull = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_body_hull.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.left_dock_container = ctk.CTkFrame(self.main_body_hull, fg_color=self.c_panel_navy, width=280, corner_radius=12, border_width=1, border_color=self.c_border_slate)
        self.left_dock_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        self.left_dock_container.pack_propagate(False)

        tech_crest = (
            "   ⚡     ⚡   \n"
            " █▀▀▀▀▀▀▀█ \n"
            "    ███    \n"
            "    ███    \n"
            "    ███    \n"
            " 🔍 TALHA 🔍 "
        )
        self.lbl_brand_crest = ctk.CTkLabel(self.left_dock_container, text=tech_crest, font=ctk.CTkFont(family="Consolas", size=15, weight="bold"), text_color=self.c_neon_blue, justify="center")
        self.lbl_brand_crest.pack(pady=(35, 20))

        self.btn_scan = ctk.CTkButton(self.left_dock_container, text="⚡ RUN DIAGNOSTIC SCAN", fg_color="transparent", border_color=self.c_neon_blue, border_width=2, text_color="#FFFFFF", font=ctk.CTkFont(size=12, weight="bold"), hover_color="#1A365D", height=42, corner_radius=21, command=self.start_async_diagnostic_scan)
        self.btn_scan.pack(fill=tk.X, padx=18, pady=6)

        btn_import_side = ctk.CTkButton(self.left_dock_container, text="📂 IMPORT PANIC LOG", fg_color="transparent", border_color=self.c_neon_blue, border_width=2, text_color="#FFFFFF", font=ctk.CTkFont(size=12, weight="bold"), hover_color="#1A365D", height=42, corner_radius=21, command=self.import_local_panic_file)
        btn_import_side.pack(fill=tk.X, padx=18, pady=6)

        btn_search = ctk.CTkButton(self.left_dock_container, text="🔍 MANUAL CODE SEARCH", fg_color="transparent", border_color=self.c_neon_blue, border_width=2, text_color="#FFFFFF", font=ctk.CTkFont(size=12, weight="bold"), hover_color="#1A365D", height=42, corner_radius=21, command=self.display_manual_search_prompt)
        btn_search.pack(fill=tk.X, padx=18, pady=6)

        btn_export = ctk.CTkButton(self.left_dock_container, text="💾 EXPORT REPORT", fg_color="transparent", border_color=self.c_neon_blue, border_width=2, text_color="#FFFFFF", font=ctk.CTkFont(size=12, weight="bold"), hover_color="#1A365D", height=42, corner_radius=21, command=self.execute_report_export)
        btn_export.pack(fill=tk.X, padx=18, pady=6)

        # ⚖️ ADDED COPYRIGHT WATERMARK TO MAIN DASHBOARD PANEL
        lbl_dashboard_copyright = ctk.CTkLabel(self.left_dock_container, text=COPYRIGHT_TEXT, font=ctk.CTkFont(size=9), text_color="#334155")
        lbl_dashboard_copyright.pack(side=tk.BOTTOM, pady=(0, 10))

        self.status_bar_pill = ctk.CTkFrame(self.left_dock_container, fg_color="#122C1E", border_color=self.c_neon_green, border_width=1, height=38, corner_radius=19)
        self.status_bar_pill.pack(fill=tk.X, side=tk.BOTTOM, padx=14, pady=10)
        self.status_bar_pill.pack_propagate(False)
        self.lbl_side_status = ctk.CTkLabel(self.status_bar_pill, text="● NO ACTIVE HARDWARE TARGET", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_neon_green, anchor="center")
        self.lbl_side_status.pack(fill=tk.BOTH, expand=True)

        self.right_vertical_splitter = tk.PanedWindow(self.main_body_hull, orient=tk.VERTICAL, bg=self.c_bg_obsidian, bd=0, sashwidth=5, sashrelief=tk.FLAT)
        self.right_vertical_splitter.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.logs_tree_panel = ctk.CTkFrame(self.right_vertical_splitter, fg_color=self.c_panel_navy, corner_radius=8, border_width=1, border_color=self.c_border_slate)
        lbl_tree_title = ctk.CTkLabel(self.logs_tree_panel, text="⚠️ DEVICES LOGS (SELECTED)", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_neon_green, anchor="w", padx=12, pady=6)
        lbl_tree_title.pack(fill=tk.X)
        self.tree_listbox = tk.Listbox(self.logs_tree_panel, bg="#0B0E14", fg=self.c_neon_blue, selectbackground="#1E293B", selectforeground="#FFFFFF", font=("Consolas", 10), bd=0, highlightthickness=0)
        self.tree_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.tree_listbox.bind("<<ListboxSelect>>", self.handle_tree_item_selection_click)

        self.raw_monitor_panel = ctk.CTkFrame(self.right_vertical_splitter, fg_color=self.c_panel_navy, corner_radius=8, border_width=1, border_color=self.c_border_slate)
        lbl_raw_title = ctk.CTkLabel(self.raw_monitor_panel, text="RAW KERNEL CRASH TRACE MONITOR STREAM", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_muted, anchor="w", padx=12, pady=6)
        lbl_raw_title.pack(fill=tk.X)
        self.txt_raw_monitor = tk.Text(self.raw_monitor_panel, bg="#0B0E14", fg=self.c_neon_green, insertbackground="#FFFFFF", font=("Consolas", 9), bd=0, wrap=tk.NONE, padx=10, pady=10)
        self.txt_raw_monitor.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.verdict_canvas_panel = ctk.CTkFrame(self.right_vertical_splitter, fg_color=self.c_panel_navy, corner_radius=8, border_width=1, border_color=self.c_border_slate)
        lbl_canvas_title = ctk.CTkLabel(self.verdict_canvas_panel, text="DIAGNOSTIC PLAIN TEXT VERDICT", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_muted, anchor="w", padx=12, pady=6)
        lbl_canvas_title.pack(fill=tk.X)
        self.txt_simple_verdict = tk.Text(self.verdict_canvas_panel, bg="#0B0E14", fg="#FFFFFF", font=("Arial", 14, "bold"), bd=0, wrap=tk.WORD, padx=16, pady=16)
        self.txt_simple_verdict.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.txt_simple_verdict.configure(state="disabled")

        self.right_vertical_splitter.add(self.logs_tree_panel, minsize=130, height=140)
        self.right_vertical_splitter.add(self.raw_monitor_panel, minsize=160, height=260)
        self.right_vertical_splitter.add(self.verdict_canvas_panel, minsize=120, height=180)

        self.clear_workbench_displays()

    def purge_session_logout_action(self):
        if os.path.exists(SESSION_FILE):
            try: os.remove(SESSION_FILE)
            except Exception: pass
        self.usb_tracking_active = False

        if getattr(sys, 'frozen', False): target_execution_args = [sys.executable]
        else: target_execution_args = [sys.executable, __file__]

        subprocess.Popen(target_execution_args, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW)
        self.destroy()
        os._exit(0)

    def live_usb_handshake_loop(self):
        last_state = None
        while self.usb_tracking_active:
            try:
                base_exec_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                info_exe = os.path.join(base_exec_dir, "ideviceinfo.exe")
                if not os.path.exists(info_exe):
                    if not shutil.which("ideviceinfo.exe"):
                        self.after(0, lambda: messagebox.showerror("Missing Dependency", "Critical missing dependency: ideviceinfo.exe could not be found. USB tracking will be disabled."))
                        self.usb_tracking_active = False
                        break
                    else:
                        info_exe = "ideviceinfo.exe"

                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                proc = subprocess.run([info_exe, "-k", "ProductType"], capture_output=True, text=True, startupinfo=startupinfo, timeout=2)

                if proc.returncode == 0 and proc.stdout.strip():
                    raw_id = proc.stdout.strip()
                    model_map = {
                        "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max",
                        "iPhone13,1": "iPhone 12 mini", "iPhone13,2": "iPhone 12", "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
                        "iPhone14,4": "iPhone 13 mini", "iPhone14,5": "iPhone 13", "iPhone14,2": "iPhone 13 Pro", "iPhone14,3": "iPhone 13 Pro Max",
                        "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
                        "iPhone15,4": "iPhone 15", "iPhone15,5": "iPhone 15 Plus", "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max",
                        "iPhone17,3": "iPhone 16", "iPhone17,4": "iPhone 16 Plus", "iPhone17,1": "iPhone 16 Pro", "iPhone17,2": "iPhone 16 Pro Max",
                        "iPhone18,1": "iPhone 17 Pro", "iPhone18,2": "iPhone 17 Pro Max"
                    }
                    self.connected_device_model = model_map.get(raw_id, f"Modern iPhone ({raw_id})")
                    self.is_device_online = True
                    current_state = "CONNECTED_" + raw_id
                else:
                    self.is_device_online = False
                    current_state = "DISCONNECTED"

                if current_state != last_state and self.usb_tracking_active:
                    last_state = current_state
                    self.after(0, lambda: self.safe_ui_synchronize_callback(self.is_device_online))

            except Exception:
                self.is_device_online = False
                if last_state != "DISCONNECTED" and self.usb_tracking_active:
                    last_state = "DISCONNECTED"
                    self.after(0, lambda: self.safe_ui_synchronize_callback(False))
            time.sleep(2.5)

    def safe_ui_synchronize_callback(self, active):
        if not self.usb_tracking_active: return
        if active:
            model_upper = self.connected_device_model.upper()
            self.badge_text.configure(text=f"● {model_upper} MOUNTED READY", text_color=self.c_neon_green)
            self.lbl_side_status.configure(text=f"● {model_upper} READY")
        else:
            if self.imported_log_content:
                self.badge_text.configure(text="● PARSING VIA IMPORTED LOG ASSET", text_color=self.c_neon_blue)
                self.lbl_side_status.configure(text="● STATIC LOG TARGET VERIFIED")
            else:
                self.badge_text.configure(text="● NO WORKBENCH TARGET LINKED", text_color=self.c_alert_crimson)
                self.lbl_side_status.configure(text="● NO ACTIVE HARDWARE TARGET")

    def import_local_panic_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Apple Panic Logs", "*.ips *.panic *.txt")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                self.imported_log_content = content
                self.selected_file_from_tree = None

                self.tree_listbox.delete(0, tk.END)
                self.tree_listbox.insert(tk.END, "📁 IMPORTED TARGET FILE")
                self.tree_listbox.insert(tk.END, f"   └── {os.path.basename(file_path)} (SELECTED)")
                self.tree_listbox.select_set(1)

                self.txt_raw_monitor.configure(state="normal")
                self.txt_raw_monitor.delete("1.0", tk.END)
                self.txt_raw_monitor.insert("1.0", content)
                self.txt_raw_monitor.configure(state="disabled")

                self.safe_ui_synchronize_callback(False)
                self.start_async_diagnostic_scan()
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to parse text asset: {str(e)}")

    def populate_extracted_device_logs_tree(self, directory_path):
        self.tree_listbox.delete(0, tk.END)
        if not os.path.exists(directory_path): return

        files = [
            f for f in os.listdir(directory_path)
            if re.match(r"^panic-full", f, re.IGNORECASE) and f.endswith(('.ips', '.panic', '.txt'))
        ]
        self.tree_listbox.insert(tk.END, f"📁 EXTRACTED PANIC FILE DATA ({self.connected_device_model}):")

        if not files:
            self.tree_listbox.insert(tk.END, "   [ No diagnostic panic logs found inside local environment ]")
            return

        for file in files:
            self.tree_listbox.insert(tk.END, f"   ├── {file}")

    def handle_tree_item_selection_click(self, event):
        selection = self.tree_listbox.curselection()
        if not selection: return
        idx = selection[0]
        item_text = self.tree_listbox.get(idx)

        if "├──" in item_text:
            file_name = item_text.split("├──")[1].strip()

            appdata_base = os.path.join(os.environ.get('APPDATA'), 'TalhaPanicAnalyzer')
            target_path = os.path.join(appdata_base, "Extracted_Panic_Logs", file_name)

            if os.path.exists(target_path):
                try:
                    with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                        self.selected_file_from_tree = f.read()

                    self.txt_raw_monitor.configure(state="normal")
                    self.txt_raw_monitor.delete("1.0", tk.END)
                    self.txt_raw_monitor.insert("1.0", self.selected_file_from_tree)
                    self.txt_raw_monitor.configure(state="disabled")

                    self.start_async_diagnostic_scan()
                except Exception as e:
                    messagebox.showerror("Read Error", str(e))

    def start_async_diagnostic_scan(self):
        self.btn_scan.configure(state="disabled", text="⚡ EXTRACTING LOGS...")
        threading.Thread(target=self.async_diagnostic_execution_worker, daemon=True).start()

    def async_diagnostic_execution_worker(self):
        try:
            active_log_source = None

            appdata_base = os.path.join(os.environ.get('APPDATA'), 'TalhaPanicAnalyzer')
            temp_stage_dir = os.path.join(appdata_base, "Talha_Stage_Cache")
            local_logs_dir = os.path.join(appdata_base, "Extracted_Panic_Logs")

            if self.selected_file_from_tree:
                active_log_source = self.selected_file_from_tree
            elif self.imported_log_content:
                active_log_source = self.imported_log_content
            elif self.is_device_online:
                base_exec_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                crash_exe = os.path.join(base_exec_dir, "idevicecrashreport.exe")
                if not os.path.exists(crash_exe):
                    if not shutil.which("idevicecrashreport.exe"):
                        self.after(0, lambda: messagebox.showerror("Missing Dependency", "Critical missing dependency: idevicecrashreport.exe could not be found. Unable to extract logs."))
                        return
                    else:
                        crash_exe = "idevicecrashreport.exe"

                if os.path.exists(temp_stage_dir): shutil.rmtree(temp_stage_dir, ignore_errors=True)
                if os.path.exists(local_logs_dir): shutil.rmtree(local_logs_dir, ignore_errors=True)

                os.makedirs(temp_stage_dir, exist_ok=True)
                os.makedirs(local_logs_dir, exist_ok=True)

                try:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    p = subprocess.Popen(
                        [crash_exe, "-e", "-k", temp_stage_dir],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        startupinfo=startupinfo,
                        cwd=base_exec_dir
                    )

                    try:
                        stdout_data, stderr_data = p.communicate(timeout=180)
                    except subprocess.TimeoutExpired:
                        p.kill()
                        stdout_data, stderr_data = p.communicate()
                    finally:
                        if p.poll() is None:
                            p.kill()

                    if "Password protected" in stderr_data or "Backup password" in stderr_data:
                        self.after(0, lambda: messagebox.showwarning("Device Locked", "🔒 EXTRACTION HALTED: Please unlock the iPhone screen passcode and verify it trusts this machine!"))

                    for root, _, files in os.walk(temp_stage_dir):
                        for file in files:
                            if re.match(r"^panic-full", file, re.IGNORECASE) and file.endswith(('.ips', '.panic', '.txt')):
                                src_file = os.path.join(root, file)
                                dest_file = os.path.join(local_logs_dir, file)
                                try: shutil.copy2(src_file, dest_file)
                                except Exception: pass

                    shutil.rmtree(temp_stage_dir, ignore_errors=True)
                    self.after(0, lambda: self.populate_extracted_device_logs_tree(local_logs_dir))

                    panic_files = [
                        os.path.join(local_logs_dir, f) for f in os.listdir(local_logs_dir)
                        if re.match(r"^panic-full", f, re.IGNORECASE) and f.endswith(('.ips', '.panic', '.txt'))
                    ]

                    if panic_files:
                        latest_file = max(panic_files, key=os.path.getmtime)
                        with open(latest_file, "r", encoding="utf-8", errors="ignore") as f:
                            active_log_source = f.read()
                except Exception:
                    pass

            self.after(0, lambda: self.finalize_diagnostic_render_pass(active_log_source))
        finally:
            self.after(0, lambda: self.btn_scan.configure(state="normal", text="⚡ RUN DIAGNOSTIC SCAN"))

    def finalize_diagnostic_render_pass(self, active_log_source):
        # State config handled by try...finally in execution worker safely.

        if not active_log_source:
            self.clear_workbench_displays()
            return

        panic_string_block = ""
        panic_match = re.search(r'"panicString"\s*:\s*"([^"]+)"', active_log_source)
        if panic_match:
            panic_string_block = panic_match.group(1).replace('\\n', '\n').replace('\\/', '/')
        else:
            panic_string_block = active_log_source

        detected_faults = []

        if "sensor array" in panic_string_block:
            array_matches = re.findall(r'sensor array.*?is\s+([0-9xXa-fA-F,\s]+)', panic_string_block)
            for match_segment in array_matches:
                extracted_tokens = re.findall(r'\b0x[0-9a-fA-F]+\b|\b\d+\b', match_segment)
                for token in extracted_tokens:
                    normalized_token = token.upper().replace('0X', '0x') if token.startswith(('0x', '0X')) else token
                    if normalized_token in BITMASK_REGISTRY and normalized_token not in ["0", "0x0"]:
                        desc = BITMASK_REGISTRY[normalized_token]
                        if desc not in detected_faults:
                            detected_faults.append(desc)

        if not detected_faults:
            for signature_key, structural_description in BITMASK_REGISTRY.items():
                if not signature_key.isdigit() and not signature_key.startswith('0x'):
                    if signature_key in panic_string_block:
                        if structural_description not in detected_faults:
                            detected_faults.append(structural_description)

        if detected_faults:
            if len(detected_faults) == 1:
                verdict_string = f"🚨 DIAGNOSTIC VERDICT:\n\n  • {detected_faults[0]}"
            else:
                verdict_string = "🚨 DIAGNOSTIC VERDICT: MULTIPLE FAULTS DETECTED\n\n"
                for fault in detected_faults:
                    verdict_string += f"  • {fault}\n"

            self.txt_simple_verdict.configure(state="normal")
            self.txt_simple_verdict.delete("1.0", tk.END)
            self.txt_simple_verdict.insert("1.0", verdict_string)
            self.c_neon_blue = "#00D2FF"
            self.txt_simple_verdict.configure(state="disabled")
        else:
            self.render_invalid_log_parse()

    def display_manual_search_prompt(self):
        dialog = ctk.CTkInputDialog(text="Enter Code / Text Phrase:", title="Manual Diagnostic Search")
        raw_val = dialog.get_input()
        if not raw_val: return
        search_target = raw_val.strip()

        if search_target.startswith(('0x', '0X')):
            search_target = search_target.lower()

        if search_target in BITMASK_REGISTRY:
            verdict_string = f"🚨 DIAGNOSTIC VERDICT:\n\n  • {BITMASK_REGISTRY[search_target]}"
            self.txt_simple_verdict.configure(state="normal")
            self.txt_simple_verdict.delete("1.0", tk.END)
            self.txt_simple_verdict.insert("1.0", verdict_string)
            self.txt_simple_verdict.configure(state="disabled")
        else:
            self.render_invalid_log_parse()

    def execute_report_export(self):
        verdict_data = self.txt_simple_verdict.get("1.0", tk.END).strip()
        if not verdict_data or "[ WORKBENCH READY" in verdict_data:
            messagebox.showwarning("Export Void", "No active diagnostic records available to export yet.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Brief", "*.txt")])
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(f"TALHA PANIC ANALYZER REPORT SUMMARY\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"──────────────────────────────────────────────────\n")
                    f.write(verdict_data)
                messagebox.showinfo("Export Perfect", f"Diagnostic brief written to:\\n{save_path}")
            except Exception as e:
                messagebox.showerror("Write Error", str(e))

    def clear_workbench_displays(self):
        self.txt_simple_verdict.configure(state="normal")
        self.txt_simple_verdict.delete("1.0", tk.END)
        self.txt_simple_verdict.insert("1.0", "[ WORKBENCH READY -> INITIALIZE DATA SCAN PATHWAY ]")
        self.txt_simple_verdict.configure(state="disabled")

    def render_invalid_log_parse(self):
        self.txt_simple_verdict.configure(state="normal")
        self.txt_simple_verdict.delete("1.0", tk.END)
        self.txt_simple_verdict.insert("1.0", "⚠️ PARSING ERROR: No valid hardware register bitmask tracking signatures found in this log.")
        self.txt_simple_verdict.configure(state="disabled")

    def close_entire_program(self):
        self.usb_tracking_active = False
        try: self.destroy()
        except Exception: pass
        os._exit(0)


if __name__ == "__main__":
    gatekeeper = LoginWindow()
    gatekeeper.after(100, lambda: check_for_mandatory_update(db, gatekeeper))
    gatekeeper.mainloop()