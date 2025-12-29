import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp
import threading
import os
import shutil

# ---------------- CONFIG ----------------
BG = "#1e1e1e"
CARD = "#2b2b2b"
ACCENT = "#0078D4"
TEXT = "#ffffff"
SUBTEXT = "#aaaaaa"

selected_folder = None

# ---------------- FIND FFMPEG ----------------
def get_ffmpeg_path():
    # 1. Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")

    # 2. Check default folder if not found
    if not ffmpeg_path:
        default_path = r"C:\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
        if os.path.exists(default_path):
            ffmpeg_path = default_path

    if not ffmpeg_path:
        raise FileNotFoundError("ffmpeg executable not found. Please install ffmpeg or add it to PATH.")

    return os.path.dirname(ffmpeg_path)

FFMPEG_PATH = get_ffmpeg_path()
print("Using ffmpeg at:", FFMPEG_PATH)

# ---------------- HELPERS ----------------
def shorten_path(path, max_len=45):
    return path if len(path) <= max_len else "..." + path[-max_len:]

def hover(widget, enter, leave):
    widget.bind("<Enter>", lambda e: widget.config(bg=enter))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave))

# ---------------- UI SETUP ----------------
root = tk.Tk()
root.title("yt2mp3")
root.geometry("520x390")
root.resizable(False, False)
root.configure(bg=BG)

# Card
card = tk.Frame(root, bg=CARD)
card.place(relx=0.5, rely=0.5, anchor="center", width=490, height=300)

# ---------------- TITLE ----------------
tk.Label(
    card, text="YT2MP3",
    font=("Segoe UI", 20, "bold"),
    bg=CARD, fg=TEXT
).pack(pady=(15, 4))

tk.Label(
    card,
    text="320 kbps • Album Art Embedded\nThe Best MP3 Downloader...\nCreated By jamiebuddychambers",
    font=("Segoe UI", 9),
    bg=CARD, fg=SUBTEXT,
    justify="center"
).pack(pady=(0, 15))

# ---------------- URL ----------------
tk.Label(card, text="YouTube URL", bg=CARD, fg=TEXT).pack(anchor="w", padx=30)

url_entry = tk.Entry(
    card, bg=BG, fg=TEXT, insertbackground=TEXT,
    font=("Segoe UI", 10), relief="flat"
)
url_entry.pack(fill="x", padx=30, pady=(5, 8))
url_entry.focus()

def focus_in(e): url_entry.config(bg="#252525")
def focus_out(e): url_entry.config(bg=BG)

url_entry.bind("<FocusIn>", focus_in)
url_entry.bind("<FocusOut>", focus_out)

# ---------------- FOLDER ----------------
def choose_folder():
    global selected_folder
    folder = filedialog.askdirectory(title="Choose download folder")
    if folder:
        selected_folder = folder
        folder_label.config(text=f"📁 {shorten_path(folder)}")

folder_btn = tk.Button(
    card, text="Choose Download Folder",
    bg="#3a3a3a", fg=TEXT,
    relief="flat", padx=10, pady=6,
    cursor="hand2",
    command=choose_folder
)
folder_btn.pack()
hover(folder_btn, "#4a4a4a", "#3a3a3a")

folder_label = tk.Label(
    card, text="📁 No folder selected",
    bg=CARD, fg=SUBTEXT,
    font=("Segoe UI", 9)
)
folder_label.pack(pady=(5, 15))

# ---------------- DOWNLOAD ----------------
def download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a URL")
        return

    if not selected_folder:
        messagebox.showerror("Error", "Choose a download folder")
        return

    download_btn.config(state="disabled")
    status.config(text="Downloading...\nPlease wait")

    def task():
        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(selected_folder, "%(title)s.%(ext)s"),
                "ffmpeg_location": FFMPEG_PATH,
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"},
                    {"key": "EmbedThumbnail"},
                    {"key": "FFmpegMetadata"},
                ],
                "writethumbnail": True,
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Done", "MP3 downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            status.config(text="Ready")
            download_btn.config(state="normal")

    threading.Thread(target=task, daemon=True).start()

download_btn = tk.Button(
    card, text="Download MP3",
    bg=ACCENT, fg=TEXT,
    font=("Segoe UI Semibold", 10),
    relief="flat", padx=20, pady=8,
    cursor="hand2",
    command=download
)
download_btn.pack(pady=5)
hover(download_btn, "#1a8cff", ACCENT)

# ---------------- STATUS ----------------
status = tk.Label(
    root,
    text="Ready\nWaiting for input",
    bg="#2a2a2a",
    fg="#bbbbbb",
    font=("Segoe UI", 9),
    height=2,
    justify="center"
)
status.pack(side="bottom", fill="x")

root.mainloop()
