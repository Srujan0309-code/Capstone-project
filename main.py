import tkinter as tk
from tkinter import ttk
import time
import math
import random
from ui_components import *
from logic import *

class RailwayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Railway Traffic Control System – AI Deadlock-Free Monitor")
        self.root.geometry("1400x900")
        self.root.configure(bg=BG_DARK)
        
        apply_ttk_theme()
        
        self.trains = []
        self.tracks = [TrackSection(f"T{i}") for i in range(8)]
        self.monitor = DeadlockMonitor(self.trains, self.tracks)
        self.simulation_mode = "detection"
        self.is_simulating = False
        
        self.last_deadlock_check = 0
        self.cached_deadlock = None
        self.track_shapes = []
        
        self._setup_layout()
        self.root.update_idletasks() # Ensure sizes are calculated
        self.draw_tracks()
        self._animate()
        self._update_stats()

    def _setup_layout(self):
        # --- Top Header ---
        self.header = tk.Frame(self.root, bg=BG_DARK, height=80)
        self.header.pack(fill="x", side="top", padx=20, pady=10)
        
        tk.Label(self.header, text="RAILWAY TRAFFIC CONTROL CENTER", 
                 font=("Inter", 24, "bold"), bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        
        self.state_label = tk.Label(self.header, text="● SYSTEM SAFE", 
                                   font=("Inter", 14, "bold"), bg=BG_DARK, fg=ACCENT_GREEN)
        self.state_label.pack(side="left", padx=50)
        
        self.clock_label = tk.Label(self.header, text="", font=("Inter", 14), bg=BG_DARK, fg=TEXT_SECONDARY)
        self.clock_label.pack(side="right")
        self._update_clock()

        # --- Main Body (Middle Section) ---
        self.main_container = tk.Frame(self.root, bg=BG_DARK)
        self.main_container.pack(fill="both", expand=True, padx=20)

        # Left Panel (Controls)
        self.left_panel = RoundedPanel(self.main_container, width=250)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        tk.Label(self.left_panel, text="COMMANDS", font=("Inter", 12, "bold"), 
                 bg=BG_PANEL, fg=TEXT_PRIMARY).place(x=20, y=20)
        
        ModernButton(self.left_panel, "ADD TRAIN", command=self.add_train).place(x=20, y=60, width=210)
        self.start_btn = ModernButton(self.left_panel, "START SIMULATION", command=self.toggle_simulation)
        self.start_btn.place(x=20, y=110, width=210)
        ModernButton(self.left_panel, "RESET", command=self.reset_system).place(x=20, y=160, width=210)
        
        tk.Label(self.left_panel, text="MODE SELECT", font=("Inter", 10, "bold"), 
                 bg=BG_PANEL, fg=TEXT_SECONDARY).place(x=20, y=220)
        
        self.mode_var = tk.StringVar(value="detection")
        for i, (m, label) in enumerate([("prone", "Deadlock-Prone"), ("detection", "Detection Mode"), ("prevention", "Prevention Mode")]):
            rb = tk.Radiobutton(self.left_panel, text=label, variable=self.mode_var, value=m,
                                command=self.change_mode, bg=BG_PANEL, fg=TEXT_SECONDARY,
                                selectcolor=BG_DARK, activebackground=BG_PANEL, font=("Inter", 10))
            rb.place(x=20, y=250 + (i*30))

        # Center Panel (Visualization)
        self.canvas_panel = RoundedPanel(self.main_container)
        self.canvas_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_panel, bg=BG_PANEL, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        self.canvas.bind("<Configure>", lambda e: self.draw_tracks())

        # Right Panel (Stats)
        self.right_panel = RoundedPanel(self.main_container, width=250)
        self.right_panel.pack(side="right", fill="y", padx=(10, 0), pady=10)
        
        tk.Label(self.right_panel, text="SYSTEM STATS", font=("Inter", 12, "bold"), 
                 bg=BG_PANEL, fg=TEXT_PRIMARY).place(x=20, y=20)
        
        self.stats = {}
        labels = ["Active Trains", "Waiting Trains", "Deadlocks Detected", "Throughput"]
        for i, text in enumerate(labels):
            tk.Label(self.right_panel, text=text, font=("Inter", 10), bg=BG_PANEL, fg=TEXT_SECONDARY).place(x=20, y=60 + (i*60))
            val = tk.Label(self.right_panel, text="0", font=("Inter", 16, "bold"), bg=BG_PANEL, fg=ACCENT_BLUE)
            val.place(x=20, y=80 + (i*60))
            self.stats[text] = val

        # --- Bottom Panel (Log) ---
        self.bottom_panel = RoundedPanel(self.root, height=150)
        self.bottom_panel.pack(fill="x", side="bottom", padx=20, pady=(0, 20))
        
        self.log_box = EventLog(self.bottom_panel)
        self.log_box.place(x=10, y=10, relwidth=0.98, relheight=0.9)
        self.log_box.log("System Initialized. Ready for simulation.", "SUCCESS")

    def _update_clock(self):
        self.clock_label.config(text=time.strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def draw_tracks(self):
        self.canvas.delete("track")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 10 or h < 10: return # Avoid drawing on collapsed canvas
        cx, cy = w/2, h/2
        r = min(w, h) * 0.35
        
        # Draw circular track layout
        self.track_shapes = []
        for i in range(len(self.tracks)):
            angle_start = i * (360/8)
            
            # Draw segment
            color = "#333" if not self.tracks[i].occupied_by else ACCENT_BLUE
            arc_id = self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=angle_start, extent=360/8, 
                                   style="arc", width=15, outline=color, tags="track")
            self.track_shapes.append(arc_id)
            
            # Label
            mid_angle = math.radians(angle_start + (360/16))
            lx, ly = cx + (r+30) * math.cos(mid_angle), cy - (r+30) * math.sin(mid_angle)
            self.canvas.create_text(lx, ly, text=self.tracks[i].id, fill=TEXT_SECONDARY, font=("Inter", 10), tags="track")

    def _update_track_colors(self):
        if not self.track_shapes: return
        for i, track in enumerate(self.tracks):
            color = "#333" if not track.occupied_by else ACCENT_BLUE
            if i < len(self.track_shapes):
                self.canvas.itemconfig(self.track_shapes[i], outline=color)

    def _animate(self):
        self.canvas.delete("train")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w/2, h/2
        r = min(w, h) * 0.35
        
        # Check Deadlock at reduced frequency (every 500ms)
        now = time.time()
        if now - self.last_deadlock_check > 0.5:
            self.cached_deadlock = self.monitor.detect_deadlock()
            self.last_deadlock_check = now

        if self.cached_deadlock:
            self.state_label.config(text="● DEADLOCK DETECTED", fg=ACCENT_RED)
            self.canvas.create_oval(cx-r-5, cy-r-5, cx+r+5, cy+r+5, outline=ACCENT_RED, width=2, tags="train")
        else:
            self.state_label.config(text="● SYSTEM SAFE", fg=ACCENT_GREEN)

        for train in self.trains:
            if train.current_index != -1:
                # Calculate smooth position (interpolation)
                angle = math.radians(train.current_index * (360/8) + (360/16))
                tx, ty = cx + r * math.cos(angle), cy - r * math.sin(angle)
                
                # Draw train icon
                color = ACCENT_GREEN if train.waiting_for is None else "#FFA500"
                self.canvas.create_oval(tx-10, ty-10, tx+10, ty+10, fill=color, outline=TEXT_PRIMARY, tags="train")
                self.canvas.create_text(tx, ty-20, text=train.train_id, fill=TEXT_PRIMARY, font=("Inter", 9, "bold"), tags="train")

        self.root.after(50, self._animate)
        self._update_track_colors()

    def _update_stats(self):
        active = sum(1 for t in self.trains if t.is_alive())
        waiting = sum(1 for t in self.trains if t.waiting_for)
        deadlock_count = 1 if self.cached_deadlock else 0 
        
        self.stats["Active Trains"].config(text=str(active))
        self.stats["Waiting Trains"].config(text=str(waiting))
        self.stats["Deadlocks Detected"].config(text=str(deadlock_count))
        
        self.root.after(500, self._update_stats)

    def add_train(self):
        tid = f"TRN-{len(self.trains)+1:02d}"
        # A train route is just all track sections in order for now
        t = Train(tid, self.tracks, mode=self.mode_var.get())
        self.trains.append(t)
        if self.is_simulating:
            t.start()
        self.log_box.log(f"Train {tid} added to fleet.", "INFO")

    def toggle_simulation(self):
        if not self.is_simulating:
            self.is_simulating = True
            self.start_btn.config(text="PAUSE SIMULATION", fg=ACCENT_RED, activebackground=ACCENT_RED)
            for t in self.trains:
                if not t.is_alive():
                    t.start()
            self.log_box.log("Simulation Started.", "SUCCESS")
        else:
            self.is_simulating = False
            self.start_btn.config(text="START SIMULATION", fg=ACCENT_BLUE, activebackground=ACCENT_BLUE)
            # In a real app we'd pause the threads, here we just stop them for simplicity if toggled
            self.log_box.log("Simulation Paused/Stopped. (Note: Threads will be cleared on Reset)", "WARNING")

    def reset_system(self):
        self.is_simulating = False
        self.start_btn.config(text="START SIMULATION", fg=ACCENT_BLUE, activebackground=ACCENT_BLUE)
        for t in self.trains:
            t.stop()
        self.trains.clear()
        for track in self.tracks:
            if track.lock.locked():
                try: track.release()
                except: pass
            track.occupied_by = None
        self.log_box.log("System Reset Complete.", "INFO")
        self.draw_tracks()

    def change_mode(self):
        mode = self.mode_var.get()
        self.log_box.log(f"Switching to {mode.upper()} mode.", "INFO")
        for t in self.trains:
            t.mode = mode

if __name__ == "__main__":
    root = tk.Tk()
    app = RailwayApp(root)
    root.mainloop()
