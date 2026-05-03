"""
Module 2: GUI / Visualization Dashboard
Thread Pool Management System - CSE316 CA2
Run this file to launch the full GUI application.
"""

import tkinter as tk
from tkinter import ttk, font
import threading
import time
import random
from thread_pool import ThreadPool, Task


# ─── Color palette ─────────────────────────────────────────────────────────
CLR_BG       = "#1E1E2E"
CLR_PANEL    = "#2A2A3E"
CLR_IDLE     = "#4CAF50"   # green
CLR_RUNNING  = "#FFC107"   # amber
CLR_TERM     = "#F44336"   # red
CLR_TEXT     = "#E0E0E0"
CLR_ACCENT   = "#7C83FD"
CLR_QUEUE    = "#29B6F6"
CLR_DONE     = "#66BB6A"


def simulate_work(task_num: int, duration: float):
    """Simulated workload for demo tasks."""
    time.sleep(duration)
    return f"Result-{task_num}"


class ThreadCard(tk.Frame):
    """Visual card representing one worker thread."""

    def __init__(self, master, thread_name: str, **kw):
        super().__init__(master, bg=CLR_PANEL, bd=2, relief="ridge", **kw)
        self.thread_name = thread_name

        self.lbl_name = tk.Label(self, text=thread_name, bg=CLR_PANEL,
                                  fg=CLR_TEXT, font=("Consolas", 9, "bold"))
        self.lbl_name.pack(pady=(6, 2))

        self.indicator = tk.Canvas(self, width=30, height=30, bg=CLR_PANEL,
                                    highlightthickness=0)
        self.indicator.pack()
        self._circle = self.indicator.create_oval(4, 4, 26, 26, fill=CLR_IDLE, outline="")

        self.lbl_state = tk.Label(self, text="IDLE", bg=CLR_PANEL,
                                   fg=CLR_IDLE, font=("Consolas", 8))
        self.lbl_state.pack(pady=(2, 4))

        self.lbl_task = tk.Label(self, text="—", bg=CLR_PANEL,
                                  fg="#888", font=("Consolas", 7), wraplength=90)
        self.lbl_task.pack(pady=(0, 6))

    def update_state(self, state: str, task_str: str = "—"):
        color_map = {"idle": CLR_IDLE, "running": CLR_RUNNING, "terminated": CLR_TERM}
        color = color_map.get(state, CLR_IDLE)
        self.indicator.itemconfig(self._circle, fill=color)
        self.lbl_state.config(text=state.upper(), fg=color)
        self.lbl_task.config(text=task_str if task_str else "—")


class ThreadPoolGUI:
    """Main GUI application window for the Thread Pool Visualizer."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Thread Pool Management System — CSE316 CA2")
        self.root.configure(bg=CLR_BG)
        self.root.geometry("900x680")
        self.root.resizable(True, True)

        self.pool: ThreadPool | None = None
        self.task_counter = 0
        self._running = False
        self.thread_cards: dict[str, ThreadCard] = {}

        self._build_ui()

    # ─── UI Construction ────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Title bar ──
        title_frame = tk.Frame(self.root, bg=CLR_ACCENT, height=50)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="⚙  Thread Pool Management System",
                 bg=CLR_ACCENT, fg="white",
                 font=("Consolas", 14, "bold")).pack(side="left", padx=16, pady=10)

        # ── Controls row ──
        ctrl = tk.Frame(self.root, bg=CLR_BG, pady=10)
        ctrl.pack(fill="x", padx=16)

        tk.Label(ctrl, text="Pool Size:", bg=CLR_BG, fg=CLR_TEXT,
                 font=("Consolas", 10)).pack(side="left")
        self.pool_size_var = tk.IntVar(value=4)
        self.pool_size_spin = tk.Spinbox(ctrl, from_=1, to=12,
                                          textvariable=self.pool_size_var,
                                          width=4, font=("Consolas", 10))
        self.pool_size_spin.pack(side="left", padx=(4, 16))

        self.btn_start = tk.Button(ctrl, text="▶  Start Pool", bg=CLR_IDLE, fg="white",
                                    font=("Consolas", 10, "bold"), relief="flat",
                                    padx=10, command=self._start_pool)
        self.btn_start.pack(side="left", padx=4)

        self.btn_stop = tk.Button(ctrl, text="■  Shutdown", bg=CLR_TERM, fg="white",
                                   font=("Consolas", 10, "bold"), relief="flat",
                                   padx=10, command=self._shutdown_pool, state="disabled")
        self.btn_stop.pack(side="left", padx=4)

        tk.Label(ctrl, text="  Task Duration (s):", bg=CLR_BG, fg=CLR_TEXT,
                 font=("Consolas", 10)).pack(side="left", padx=(20, 0))
        self.duration_var = tk.DoubleVar(value=1.0)
        self.duration_slider = tk.Scale(ctrl, from_=0.2, to=4.0, resolution=0.2,
                                         orient="horizontal", variable=self.duration_var,
                                         bg=CLR_BG, fg=CLR_TEXT, highlightthickness=0,
                                         troughcolor=CLR_PANEL, length=120)
        self.duration_slider.pack(side="left")

        self.btn_submit = tk.Button(ctrl, text="+ Submit Task", bg=CLR_ACCENT, fg="white",
                                     font=("Consolas", 10, "bold"), relief="flat",
                                     padx=10, command=self._submit_task, state="disabled")
        self.btn_submit.pack(side="left", padx=(16, 4))

        self.btn_submit5 = tk.Button(ctrl, text="+ Submit 5", bg=CLR_QUEUE, fg="white",
                                      font=("Consolas", 10, "bold"), relief="flat",
                                      padx=10, command=lambda: [self._submit_task() for _ in range(5)],
                                      state="disabled")
        self.btn_submit5.pack(side="left", padx=4)

        # ── Resize controls ──
        resize_frame = tk.Frame(self.root, bg=CLR_BG)
        resize_frame.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(resize_frame, text="Resize Pool:", bg=CLR_BG, fg=CLR_TEXT,
                 font=("Consolas", 9)).pack(side="left")
        self.resize_var = tk.IntVar(value=4)
        tk.Spinbox(resize_frame, from_=1, to=12, textvariable=self.resize_var,
                   width=4, font=("Consolas", 9)).pack(side="left", padx=4)
        tk.Button(resize_frame, text="Apply Resize", bg=CLR_PANEL, fg=CLR_TEXT,
                  font=("Consolas", 9), relief="flat",
                  command=self._resize_pool).pack(side="left", padx=4)

        # ── Main area: thread cards + stats ──
        main = tk.Frame(self.root, bg=CLR_BG)
        main.pack(fill="both", expand=True, padx=16)

        # Thread cards panel
        tk.Label(main, text="Worker Threads", bg=CLR_BG, fg=CLR_ACCENT,
                 font=("Consolas", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.cards_frame = tk.Frame(main, bg=CLR_BG)
        self.cards_frame.grid(row=1, column=0, sticky="nsew")

        # Stats panel
        tk.Label(main, text="Statistics", bg=CLR_BG, fg=CLR_ACCENT,
                 font=("Consolas", 11, "bold")).grid(row=0, column=1, sticky="w",
                                                      padx=(20, 0), pady=(0, 4))
        stats_panel = tk.Frame(main, bg=CLR_PANEL, bd=1, relief="solid")
        stats_panel.grid(row=1, column=1, sticky="nsew", padx=(20, 0))

        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)

        labels = ["Submitted", "Started", "Completed", "Queue Size",
                  "Avg Wait (s)", "Avg Exec (s)"]
        self.stat_vars = {l: tk.StringVar(value="0") for l in labels}
        for i, lbl in enumerate(labels):
            tk.Label(stats_panel, text=lbl + ":", bg=CLR_PANEL, fg="#AAA",
                     font=("Consolas", 9)).grid(row=i, column=0, sticky="w", padx=10, pady=4)
            tk.Label(stats_panel, textvariable=self.stat_vars[lbl], bg=CLR_PANEL,
                     fg=CLR_TEXT, font=("Consolas", 10, "bold")).grid(row=i, column=1,
                                                                        sticky="e", padx=10)

        # Log panel
        tk.Label(self.root, text="Activity Log", bg=CLR_BG, fg=CLR_ACCENT,
                 font=("Consolas", 10, "bold")).pack(anchor="w", padx=16, pady=(8, 2))
        log_frame = tk.Frame(self.root, bg=CLR_BG)
        log_frame.pack(fill="x", padx=16, pady=(0, 12))
        self.log_box = tk.Text(log_frame, height=6, bg=CLR_PANEL, fg=CLR_TEXT,
                                font=("Consolas", 8), state="disabled",
                                relief="flat", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scrollbar.set)
        self.log_box.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ─── Actions ────────────────────────────────────────────────────────────

    def _start_pool(self):
        size = self.pool_size_var.get()
        self.pool = ThreadPool(pool_size=size)
        self.pool.start()
        self._running = True
        self._rebuild_cards()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_submit.config(state="normal")
        self.btn_submit5.config(state="normal")
        self._log(f"Pool started with {size} worker threads.")
        self._refresh_loop()

    def _shutdown_pool(self):
        if self.pool:
            self._running = False
            threading.Thread(target=self._do_shutdown, daemon=True).start()

    def _do_shutdown(self):
        self.pool.shutdown(wait=True)
        self.root.after(0, self._on_shutdown_complete)

    def _on_shutdown_complete(self):
        self._log("Pool shutdown complete.")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.btn_submit.config(state="disabled")
        self.btn_submit5.config(state="disabled")
        self._update_cards()

    def _submit_task(self):
        if not self.pool:
            return
        self.task_counter += 1
        duration = self.duration_var.get()
        n = self.task_counter
        self.pool.submit(simulate_work, args=(n, duration), duration=0)
        self._log(f"Task #{n} submitted (duration={duration}s)")

    def _resize_pool(self):
        if not self.pool:
            return
        new_size = self.resize_var.get()
        self.pool.resize(new_size)
        self._rebuild_cards()
        self._log(f"Pool resized to {new_size} workers.")

    def _rebuild_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        self.thread_cards.clear()
        if not self.pool:
            return
        for i, worker in enumerate(self.pool.workers):
            card = ThreadCard(self.cards_frame, worker.name, width=110, height=110)
            card.grid(row=i // 4, column=i % 4, padx=6, pady=6, sticky="nsew")
            self.thread_cards[worker.name] = card

    def _update_cards(self):
        if not self.pool:
            return
        for worker in self.pool.workers:
            if worker.name in self.thread_cards:
                task_str = str(worker.current_task) if worker.current_task else "—"
                self.thread_cards[worker.name].update_state(worker.state, task_str)
            else:
                # New worker added via resize
                self._rebuild_cards()
                break

    def _update_stats(self):
        if not self.pool:
            return
        s = self.pool.stats
        p = self.pool.get_performance_stats()
        self.stat_vars["Submitted"].set(str(s["tasks_submitted"]))
        self.stat_vars["Started"].set(str(s["tasks_started"]))
        self.stat_vars["Completed"].set(str(s["tasks_completed"]))
        self.stat_vars["Queue Size"].set(str(self.pool.task_queue.qsize()))
        self.stat_vars["Avg Wait (s)"].set(str(p.get("avg_wait_time", "—")))
        self.stat_vars["Avg Exec (s)"].set(str(p.get("avg_exec_time", "—")))

    def _refresh_loop(self):
        if not self._running:
            return
        self._update_cards()
        self._update_stats()
        self.root.after(400, self._refresh_loop)

    def _log(self, msg: str):
        self.log_box.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")


def main():
    root = tk.Tk()
    app = ThreadPoolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
