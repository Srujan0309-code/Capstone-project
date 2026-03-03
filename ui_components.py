import tkinter as tk
from tkinter import ttk
import time

# --- Theme Constants ---
BG_DARK = "#121212"
BG_PANEL = "#1E1E1E"
ACCENT_BLUE = "#00D4FF"
ACCENT_GREEN = "#39FF14"
ACCENT_RED = "#FF3131"
TEXT_PRIMARY = "#E0E0E0"
TEXT_SECONDARY = "#B0B0B0"

class RoundedPanel(tk.Canvas):
    """A canvas-based rounded panel to simulate a modern look."""
    def __init__(self, parent, bg=BG_PANEL, radius=20, **kwargs):
        super().__init__(parent, bg=BG_DARK, highlightthickness=0, **kwargs)
        self.radius = radius
        self.panel_color = bg
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = self.radius
        
        # Draw rounded rectangle
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=self.panel_color, outline=self.panel_color)
        self.create_arc((w-r*2, 0, w, r*2), start=0, extent=90, fill=self.panel_color, outline=self.panel_color)
        self.create_arc((0, h-r*2, r*2, h), start=180, extent=90, fill=self.panel_color, outline=self.panel_color)
        self.create_arc((w-r*2, h-r*2, w, h), start=270, extent=90, fill=self.panel_color, outline=self.panel_color)
        
        self.create_rectangle((r, 0, w-r, h), fill=self.panel_color, outline=self.panel_color)
        self.create_rectangle((0, r, w, h-r), fill=self.panel_color, outline=self.panel_color)

class ModernButton(tk.Button):
    """Custom button with dark theme/neon styling."""
    def __init__(self, parent, text, color=ACCENT_BLUE, **kwargs):
        super().__init__(parent, text=text, bg=BG_DARK, fg=color, 
                         activebackground=color, activeforeground=BG_DARK,
                         font=("Inter", 10, "bold"), bd=1, relief="flat",
                         highlightbackground=color, highlightcolor=color,
                         padx=10, pady=5, **kwargs)
        self.bind("<Enter>", lambda e: self.config(bg=color, fg=BG_DARK))
        self.bind("<Leave>", lambda e: self.config(bg=BG_DARK, fg=color))

class EventLog(tk.Frame):
    """A scrollable event log for system messages."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.text = tk.Text(self, bg=BG_DARK, fg=TEXT_SECONDARY, 
                            font=("Consolas", 10), bd=0, highlightthickness=1, 
                            highlightbackground="#333", padx=10, pady=10)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        
        self.text.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.text.config(state="disabled")

    def log(self, message, type="INFO"):
        self.text.config(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        color = TEXT_SECONDARY
        if type == "WARNING": color = ACCENT_RED
        elif type == "SUCCESS": color = ACCENT_GREEN
        
        tag_name = f"tag_{time.time()}"
        self.text.insert("end", f"[{timestamp}] ", "dim")
        self.text.insert("end", f"{message}\n", tag_name)
        self.text.tag_config("dim", foreground="#555")
        self.text.tag_config(tag_name, foreground=color)
        self.text.see("end")
        self.text.config(state="disabled")

def apply_ttk_theme():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TProgressbar", thickness=10, background=ACCENT_BLUE, bordercolor=BG_DARK, lightcolor=ACCENT_BLUE, darkcolor=ACCENT_BLUE)
    style.configure("Vertical.TScrollbar", gripcount=0, background="#333", darkcolor="#333", lightcolor="#333", bordercolor="#333", arrowcolor=TEXT_SECONDARY)
