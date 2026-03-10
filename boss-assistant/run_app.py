"""
Boss Assistant — desktop launcher.
Starts the server in the background and shows a small window with Open / Stop.
No PowerShell, no console to keep open. Double-click Start_Boss_Assistant.vbs (or .bat).
"""
import os
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

PORT = 8001
BASE_URL = f"http://localhost:{PORT}"
ROOT = Path(__file__).resolve().parent
LOG_FILE = ROOT / "run_app.log"


def _log(msg: str) -> None:
    """Write a line to run_app.log so we can see errors."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def _load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass


def run_server(ready_flag: list) -> subprocess.Popen | None:
    """Start uvicorn in a subprocess. ready_flag is set to True when we consider it ready."""
    python = sys.executable
    # Run from project root so imports and clients.json resolve
    cmd = [python, "-m", "uvicorn", "chat_server:app", "--host", "0.0.0.0", "--port", str(PORT)]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception as e:
        ready_flag.append(("error", str(e)))
        return None
    ready_flag.append(("started", proc))
    return proc


def open_browser():
    webbrowser.open(BASE_URL)


def main():
    _load_env()
    ready_flag: list = []
    server_proc: subprocess.Popen | None = None

    def start_server():
        nonlocal server_proc
        server_proc = run_server(ready_flag)
        if server_proc is not None:
            time.sleep(2)
            ready_flag.append(("ready", True))

    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError:
        # Fallback: no GUI, just start server and open browser
        while not any(r[0] == "ready" for r in ready_flag) and not any(r[0] == "error" for r in ready_flag):
            time.sleep(0.2)
        if any(r[0] == "error" for r in ready_flag):
            err = next(r[1] for r in ready_flag if r[0] == "error")
            print("Server failed:", err, file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
        open_browser()
        print("Server running at", BASE_URL, "- close this window to stop (or run Stop script)")
        try:
            proc = next(r[1] for r in ready_flag if r[0] == "started")
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
        return

    root = tk.Tk()
    root.title("Boss Assistant")
    root.geometry("320x150")
    root.resizable(False, False)
    root.configure(bg="#1a1a1a")

    status = tk.StringVar(value="Starting server…")
    label = tk.Label(root, textvariable=status, fg="#e8e8e8", bg="#1a1a1a", font=("Segoe UI", 10))
    label.pack(pady=(24, 12))

    def on_open():
        open_browser()

    def on_stop():
        nonlocal server_proc
        if server_proc is not None:
            try:
                server_proc.terminate()
                server_proc.wait(timeout=5)
            except Exception:
                server_proc.kill()
            server_proc = None
        root.quit()
        root.destroy()
        os._exit(0)

    def check_ready():
        for r in ready_flag:
            if r[0] == "error":
                status.set("Error: " + str(r[1])[:60])
                messagebox.showerror("Boss Assistant", "Server failed to start.\n\n" + str(r[1]))
                return
            if r[0] == "ready":
                status.set("Server running at " + BASE_URL)
                open_browser()
                return
        root.after(200, check_ready)

    root.after(200, check_ready)

    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)
    ttk.Style().configure("TButton", padding=6)
    ttk.Button(btn_frame, text="Open in browser", command=on_open).pack(side=tk.LEFT, padx=4)
    ttk.Button(btn_frame, text="Stop server", command=on_stop).pack(side=tk.LEFT, padx=4)

    root.protocol("WM_DELETE_WINDOW", on_stop)
    root.mainloop()
    on_stop()


def _show_error_and_exit(msg: str, log_path: Path) -> None:
    """Show error in a message box and exit. Works even when run with pythonw (no console)."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Boss Assistant — Error",
            msg + "\n\nDetails in: " + str(log_path),
        )
        root.destroy()
    except Exception:
        pass
    sys.exit(1)


if __name__ == "__main__":
    try:
        _log("--- run_app.py started ---")
        _log("ROOT=" + str(ROOT))
        _log("sys.executable=" + str(sys.executable))
        main()
    except Exception as e:
        err = traceback.format_exc()
        _log("CRASH: " + err)
        _show_error_and_exit(str(e)[:200], LOG_FILE)
