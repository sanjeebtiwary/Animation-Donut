import math
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parents[1]
DONUT_DIR = ROOT / "Donut"
CONTROL_FILE = DONUT_DIR / "donut_controls.txt"
CPP_SOURCE = DONUT_DIR / "donut_animation.cpp"
CPP_BINARY = DONUT_DIR / "donut_animation.exe"


def build_control_packet(mode="auto", rotate_x=0.0, rotate_y=0.0, rotate_z=0.0, zoom=1.0, speed=1.0):
    return {
        "mode": mode,
        "rotate_x": float(rotate_x),
        "rotate_y": float(rotate_y),
        "rotate_z": float(rotate_z),
        "zoom": float(zoom),
        "speed": float(speed),
    }


def write_control_packet(packet):
    DONUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CONTROL_FILE.exists():
        CONTROL_FILE.touch()
    with CONTROL_FILE.open("w", encoding="utf-8") as handle:
        for key in ("mode", "rotate_x", "rotate_y", "rotate_z", "zoom", "speed"):
            handle.write(f"{key}={packet[key]}\n")


def find_compiler():
    candidates = [
        "g++",
        os.environ.get("CXX", ""),
        r"C:\msys64\mingw64\bin\g++.exe",
        r"C:\MinGW\bin\g++.exe",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            subprocess.run([candidate, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return candidate
        except Exception:
            continue
    return None


def ensure_cpp_binary():
    if CPP_BINARY.exists():
        return str(CPP_BINARY)

    compiler = find_compiler()
    if compiler is None:
        raise RuntimeError("No C++ compiler found. Install MinGW/MSYS2 and add g++ to PATH.")

    result = subprocess.run([
        compiler,
        "-std=c++17",
        "-O2",
        str(CPP_SOURCE),
        "-lmingw32",
        "-lSDL2main",
        "-lSDL2",
        "-lOpenGL32",
        "-lglu32",
        "-o",
        str(CPP_BINARY),
    ], capture_output=True, text=True)

    if result.returncode != 0:
        details = (result.stderr or result.stdout or "compiler error").strip()
        raise RuntimeError(f"C++ compilation failed: {details}")

    return str(CPP_BINARY)


class DonutLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Donut 3D Controller")
        self.geometry("820x620")
        self.configure(bg="#091722")

        self.process = None
        self.fallback_canvas = None
        self.fallback_loop = False
        self.rotate_x = tk.DoubleVar(value=0.9)
        self.rotate_y = tk.DoubleVar(value=0.0)
        self.rotate_z = tk.DoubleVar(value=0.0)
        self.zoom = tk.DoubleVar(value=1.0)
        self.speed = tk.DoubleVar(value=1.2)
        self.auto_rotate = tk.BooleanVar(value=True)

        self.build_ui()
        self.apply_controls()
        self.start_renderer()

    def build_ui(self):
        title = tk.Label(self, text="3D Donut Studio", font=("Segoe UI", 20, "bold"), bg="#091722", fg="#dff7ff")
        title.pack(pady=(18, 12))

        panel = tk.Frame(self, bg="#112635", padx=16, pady=16)
        panel.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))

        self.add_slider(panel, "X Rotation", self.rotate_x, -3.0, 3.0)
        self.add_slider(panel, "Y Rotation", self.rotate_y, -3.0, 3.0)
        self.add_slider(panel, "Z Rotation", self.rotate_z, -3.0, 3.0)
        self.add_slider(panel, "Zoom", self.zoom, 0.5, 2.5)
        self.add_slider(panel, "Speed", self.speed, 0.2, 2.5)

        check = tk.Checkbutton(
            panel,
            text="Auto spin",
            variable=self.auto_rotate,
            command=self.apply_controls,
            bg="#112635",
            fg="#dff7ff",
            activebackground="#112635",
            activeforeground="#dff7ff",
            selectcolor="#091722",
        )
        check.pack(anchor="w", pady=(10, 10))

        buttons = tk.Frame(panel, bg="#112635")
        buttons.pack(fill=tk.X, pady=(10, 0))

        tk.Button(buttons, text="Start Render", command=self.start_renderer, bg="#29b67a", fg="white", width=16).pack(side=tk.LEFT, padx=8)
        tk.Button(buttons, text="Pause Render", command=self.stop_renderer, bg="#f4b942", fg="black", width=16).pack(side=tk.LEFT, padx=8)
        tk.Button(buttons, text="Exit", command=self.on_exit, bg="#ea526f", fg="white", width=16).pack(side=tk.LEFT, padx=8)

        self.status = tk.Label(self, text="Starting renderer...", bg="#091722", fg="#9fe6ff", font=("Segoe UI", 10))
        self.status.pack(side=tk.BOTTOM, pady=(0, 10))

    def add_slider(self, parent, label, variable, low, high):
        frame = tk.Frame(parent, bg="#112635")
        frame.pack(fill=tk.X, pady=8)

        tk.Label(frame, text=label, bg="#112635", fg="#dff7ff", width=14, anchor="w").pack(side=tk.LEFT)
        slider = ttk.Scale(frame, from_=low, to=high, variable=variable, orient=tk.HORIZONTAL, length=500)
        slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        variable.trace_add("write", lambda *_: self.apply_controls())
        slider.bind("<ButtonRelease-1>", lambda *_: self.apply_controls())

    def apply_controls(self):
        packet = build_control_packet(
            mode="auto" if self.auto_rotate.get() else "manual",
            rotate_x=self.rotate_x.get(),
            rotate_y=self.rotate_y.get(),
            rotate_z=self.rotate_z.get(),
            zoom=self.zoom.get(),
            speed=self.speed.get(),
        )
        write_control_packet(packet)

    def start_renderer(self):
        if self.process is not None and self.process.poll() is None:
            self.status.config(text="Renderer already running")
            return

        try:
            binary = ensure_cpp_binary()
            self.process = subprocess.Popen([binary], cwd=str(ROOT), creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            self.status.config(text="C++ renderer running")
            self.stop_fallback_preview()
        except Exception as exc:
            self.status.config(text=f"C++ renderer unavailable: {exc}. Using Python fallback.")
            self.start_fallback_preview()

    def stop_renderer(self):
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                pass
        self.process = None
        self.status.config(text="Renderer paused")

    def start_fallback_preview(self):
        if self.fallback_canvas is not None:
            return
        self.fallback_loop = True
        self.fallback_canvas = tk.Canvas(self, width=720, height=340, bg="#091722", highlightthickness=0)
        self.fallback_canvas.pack(pady=(12, 0))
        self.after(30, self.animate_fallback)

    def stop_fallback_preview(self):
        self.fallback_loop = False
        if self.fallback_canvas is not None:
            self.fallback_canvas.destroy()
            self.fallback_canvas = None

    def animate_fallback(self):
        if not self.fallback_loop or self.fallback_canvas is None:
            return

        self.fallback_canvas.delete("all")

        cx = 360
        cy = 170
        radius = 110 * self.zoom.get()
        spin = self.speed.get() * 0.12
        for i in range(260):
            angle = (i / 260.0) * (math.pi * 2.0) + self.rotate_y.get() + spin
            x = cx + (radius + 26 * math.sin(angle * 3.0 + self.rotate_x.get())) * math.cos(angle)
            y = cy + 62 * math.sin(angle * 2.0 + self.rotate_z.get())
            self.fallback_canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#7ef9ff", outline="#7ef9ff")

        self.after(30, self.animate_fallback)

    def on_exit(self):
        self.stop_renderer()
        self.fallback_loop = False
        if self.fallback_canvas is not None:
            self.fallback_canvas.destroy()
            self.fallback_canvas = None
        self.destroy()


if __name__ == "__main__":
    if not CONTROL_FILE.exists():
        write_control_packet(build_control_packet())
    app = DonutLauncher()
    app.mainloop()
