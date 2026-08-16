import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import sys
from pathlib import Path

APP_TITLE = "工作！！别他妈玩了！"


def resource_path(name: str) -> Path:
    """兼容源码运行和 PyInstaller onefile 打包后的资源路径。"""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def format_hms(total_seconds: float) -> str:
    total_seconds = max(0, int(total_seconds))
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_data_file() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        folder = Path(appdata) / "工作别玩了"
    else:
        folder = Path.home() / ".work_stop_playing"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "history.json"


class WorkTimerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("355x375")
        self.root.resizable(False, False)

        self._icon_ref = None
        try:
            png = resource_path("icon.png")
            self._icon_ref = tk.PhotoImage(file=str(png))
            self.root.iconphoto(True, self._icon_ref)
        except Exception:
            try:
                self.root.iconbitmap(str(resource_path("icon.ico")))
            except Exception:
                pass

        self.data_file = get_data_file()
        self.history = self.load_history()

        self.work_running = False
        self.work_elapsed = 0.0
        self.work_started_at = None
        self.segment_started_at = None

        self.countdown_running = False
        self.countdown_remaining = 0.0
        self.countdown_started_at = None
        self.countdown_started_remaining = 0.0

        self.build_ui()
        self.update_loop()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_history(self):
        data = {"last_work_seconds": 0, "records": []}
        try:
            if self.data_file.exists():
                loaded = json.loads(self.data_file.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    data.update(loaded)
        except Exception:
            pass
        return data

    def save_history_file(self):
        try:
            self.data_file.write_text(
                json.dumps(self.history, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    def save_work_record(self, seconds: float):
        seconds = max(0, int(seconds))
        if seconds <= 0:
            return

        self.history["last_work_seconds"] = seconds
        records = self.history.setdefault("records", [])
        records.append({
            "duration_seconds": seconds,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        self.history["records"] = records[-100:]
        self.save_history_file()
        self.last_work_var.set(f"上次工作：{format_hms(seconds)}")

    def build_ui(self):
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text=APP_TITLE,
            font=("Microsoft YaHei UI", 15, "bold"),
            anchor="center",
        ).pack(fill="x", pady=(0, 10))

        work_group = ttk.LabelFrame(outer, text="工作计时", padding=10)
        work_group.pack(fill="x")

        self.work_time_var = tk.StringVar(value="00:00:00")
        ttk.Label(
            work_group,
            textvariable=self.work_time_var,
            font=("Consolas", 28, "bold"),
            anchor="center",
        ).pack(fill="x", pady=(2, 5))

        last_seconds = int(self.history.get("last_work_seconds", 0) or 0)
        self.last_work_var = tk.StringVar(
            value=f"上次工作：{format_hms(last_seconds)}"
        )
        ttk.Label(
            work_group,
            textvariable=self.last_work_var,
            font=("Microsoft YaHei UI", 10),
            anchor="center",
        ).pack(fill="x", pady=(0, 8))

        self.work_button = ttk.Button(
            work_group, text="继续工作", command=self.toggle_work_timer
        )
        self.work_button.pack(fill="x")

        countdown_group = ttk.LabelFrame(outer, text="倒计时", padding=10)
        countdown_group.pack(fill="x", pady=(12, 0))

        picker = ttk.Frame(countdown_group)
        picker.pack()

        ttk.Label(picker, text="时").grid(row=0, column=0, padx=(0, 3))
        ttk.Label(picker, text="分").grid(row=0, column=2, padx=(8, 3))
        ttk.Label(picker, text="秒").grid(row=0, column=4, padx=(8, 3))

        self.hours_var = tk.IntVar(value=0)
        self.minutes_var = tk.IntVar(value=25)
        self.seconds_var = tk.IntVar(value=0)

        ttk.Spinbox(
            picker, from_=0, to=99, width=4,
            textvariable=self.hours_var, justify="center"
        ).grid(row=0, column=1)
        ttk.Spinbox(
            picker, from_=0, to=59, width=4,
            textvariable=self.minutes_var, justify="center"
        ).grid(row=0, column=3)
        ttk.Spinbox(
            picker, from_=0, to=59, width=4,
            textvariable=self.seconds_var, justify="center"
        ).grid(row=0, column=5)

        self.countdown_var = tk.StringVar(value="00:25:00")
        ttk.Label(
            countdown_group,
            textvariable=self.countdown_var,
            font=("Consolas", 20, "bold"),
            anchor="center",
        ).pack(fill="x", pady=(8, 6))

        buttons = ttk.Frame(countdown_group)
        buttons.pack(fill="x")

        self.countdown_button = ttk.Button(
            buttons, text="开始倒计时", command=self.toggle_countdown
        )
        self.countdown_button.pack(side="left", fill="x", expand=True)

        ttk.Button(
            buttons, text="重置", command=self.reset_countdown
        ).pack(side="left", padx=(8, 0))

        ttk.Label(
            outer,
            text="最小化或切到其他软件时，计时仍然继续。",
            font=("Microsoft YaHei UI", 9),
            anchor="center",
        ).pack(fill="x", pady=(10, 0))

    def toggle_work_timer(self):
        if self.work_running:
            now = time.monotonic()
            self.work_elapsed += now - self.work_started_at

            segment_seconds = now - self.segment_started_at
            self.save_work_record(segment_seconds)

            self.work_started_at = None
            self.segment_started_at = None
            self.work_running = False
            self.work_button.config(text="继续工作")
        else:
            now = time.monotonic()
            self.work_started_at = now
            self.segment_started_at = now
            self.work_running = True
            self.work_button.config(text="休息一下")

    def current_work_elapsed(self):
        value = self.work_elapsed
        if self.work_running and self.work_started_at is not None:
            value += time.monotonic() - self.work_started_at
        return value

    def picker_seconds(self):
        try:
            h = max(0, int(self.hours_var.get()))
            m = max(0, min(59, int(self.minutes_var.get())))
            s = max(0, min(59, int(self.seconds_var.get())))
            return h * 3600 + m * 60 + s
        except Exception:
            return 0

    def toggle_countdown(self):
        if self.countdown_running:
            elapsed = time.monotonic() - self.countdown_started_at
            self.countdown_remaining = max(
                0.0, self.countdown_started_remaining - elapsed
            )
            self.countdown_started_at = None
            self.countdown_running = False
            self.countdown_button.config(text="继续倒计时")
            return

        if self.countdown_remaining <= 0:
            selected = self.picker_seconds()
            if selected <= 0:
                messagebox.showwarning(APP_TITLE, "请先设置一个大于 0 的倒计时时间。")
                return
            self.countdown_remaining = float(selected)

        self.countdown_started_remaining = self.countdown_remaining
        self.countdown_started_at = time.monotonic()
        self.countdown_running = True
        self.countdown_button.config(text="暂停倒计时")

    def current_countdown_remaining(self):
        if not self.countdown_running:
            return self.countdown_remaining
        return max(
            0.0,
            self.countdown_started_remaining
            - (time.monotonic() - self.countdown_started_at)
        )

    def reset_countdown(self):
        self.countdown_running = False
        self.countdown_started_at = None
        self.countdown_remaining = float(self.picker_seconds())
        self.countdown_started_remaining = self.countdown_remaining
        self.countdown_button.config(text="开始倒计时")
        self.countdown_var.set(format_hms(self.countdown_remaining))

    def finish_countdown(self):
        self.countdown_running = False
        self.countdown_started_at = None
        self.countdown_remaining = 0.0
        self.countdown_button.config(text="开始倒计时")
        self.root.bell()
        messagebox.showinfo(APP_TITLE, "倒计时结束。")

    def on_close(self):
        if self.work_running and self.segment_started_at is not None:
            self.save_work_record(time.monotonic() - self.segment_started_at)
        self.root.destroy()

    def update_loop(self):
        self.work_time_var.set(format_hms(self.current_work_elapsed()))

        remaining = self.current_countdown_remaining()
        if self.countdown_running and remaining <= 0:
            self.countdown_var.set("00:00:00")
            self.finish_countdown()
        else:
            self.countdown_var.set(format_hms(remaining))

        self.root.after(100, self.update_loop)


if __name__ == "__main__":
    root = tk.Tk()
    WorkTimerApp(root)
    root.mainloop()
