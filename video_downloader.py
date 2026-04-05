import customtkinter as ctk
import yt_dlp
import os
import threading
import webbrowser
from PIL import Image, ImageTk

class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Updated window title
        self.title("Useful_iron223's video Downloader")
        self.geometry("800x700")
        self.minsize(600, 500)
        ctk.set_appearance_mode("dark")

        # Linux-compatible Icon Logic
        icon_path = "/home/mohammed/Downloads/app_icon.png"
        if os.path.exists(icon_path):
            try:
                pil_img = Image.open(icon_path)
                self.icon_photo = ImageTk.PhotoImage(pil_img)
                self.wm_iconphoto(True, self.icon_photo)
            except Exception as e:
                print(f"Icon error: {e}")

        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header using the new name
        self.title_label = ctk.CTkLabel(self, text="USEFUL_IRON223'S DOWNLOADER", font=("Arial", 24, "bold"), text_color="#CC00CC")
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # Main Body
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=1, column=0, padx=30, pady=20, sticky="nsew")
        
        for i in range(7):
            self.main_frame.grid_rowconfigure(i, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Paste YouTube URL here", height=45, corner_radius=15)
        self.url_entry.grid(row=0, column=0, padx=30, pady=10, sticky="ew")

        self.analyze_button = ctk.CTkButton(self.main_frame, text="1. ANALYZE LINK", command=self.start_analyze_thread, 
                                           fg_color="#9900CC", hover_color="#770099", height=45, corner_radius=15, font=("Arial", 14, "bold"))
        self.analyze_button.grid(row=1, column=0, padx=30, pady=10, sticky="ew")

        self.results_label = ctk.CTkLabel(self.main_frame, text="Resolutions: -- | FPS: --", text_color="#00FFFF", font=("Arial", 16))
        self.results_label.grid(row=2, column=0, pady=5, sticky="nsew")

        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.settings_frame.grid(row=3, column=0, sticky="nsew", padx=20)
        self.settings_frame.grid_columnconfigure((0, 1), weight=1)

        self.res_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="Resolution (e.g. 1080)", height=40, corner_radius=12)
        self.res_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.fps_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="FPS (e.g. 60)", height=40, corner_radius=12)
        self.fps_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.download_button = ctk.CTkButton(self.main_frame, text="2. START DOWNLOAD", command=self.start_download_thread, 
                                            fg_color="#0066CC", hover_color="#0055AA", height=60, corner_radius=15, font=("Arial", 18, "bold"))
        self.download_button.grid(row=4, column=0, padx=30, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", text_color="#00FF00", font=("Arial", 15, "italic"))
        self.status_label.grid(row=5, column=0, pady=5, sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=20, corner_radius=10)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=6, column=0, padx=40, pady=(10, 30), sticky="ew")

        # Clickable Credit Link
        self.credits_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.credits_frame.grid(row=2, column=0, pady=15)
        
        self.credits_static = ctk.CTkLabel(self.credits_frame, text="Credits: ", text_color="#AAAAAA", font=("Arial", 12))
        self.credits_static.pack(side="left")

        self.credits_link = ctk.CTkLabel(self.credits_frame, text="useful_iron223", text_color="#1F6AA5", font=("Arial", 12, "underline"), cursor="hand2")
        self.credits_link.pack(side="left")
        self.credits_link.bind("<Button-1>", lambda e: webbrowser.open("https://guns.lol/useful_iron223"))

    def my_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            percentage = downloaded / total
            self.progress_bar.set(percentage)
            
            raw_speed = d.get('_speed_str', '0B/s').strip()
            clean_speed = raw_speed.replace('\x1b[0;32m', '').replace('\x1b[0m', '').replace('MiB', 'MB').replace('KiB', 'KB').strip()
            self.status_label.configure(text=f"Downloading: {int(percentage*100)}% | Speed: {clean_speed}", text_color="#FFFFFF")

    def run_analyze(self):
        url = self.url_entry.get()
        if not url: return
        self.status_label.configure(text="Analyzing streams...", text_color="#FFFF00")
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                res_list = sorted(set(f.get('height') for f in formats if f.get('height') and f.get('height') >= 144), reverse=True)
                fps_list = sorted(set(int(f.get('fps')) for f in formats if f.get('fps') and f.get('fps') >= 1), reverse=True)
                
                self.results_label.configure(text=f"Available Res: {', '.join([str(r) for r in res_list[:6]])}\nAvailable FPS: {', '.join([str(f) for f in fps_list[:6]])}")
                self.status_label.configure(text="Analysis complete.", text_color="#00FF00")
                
                if res_list: self.res_entry.delete(0, 'end'); self.res_entry.insert(0, str(res_list[0]))
                if fps_list: self.fps_entry.delete(0, 'end'); self.fps_entry.insert(0, str(fps_list[0]))
        except Exception as e:
            self.status_label.configure(text=f"Analysis Error: {str(e)}", text_color="#FF0000")
        self.analyze_button.configure(state="normal")

    def start_analyze_thread(self):
        self.analyze_button.configure(state="disabled")
        threading.Thread(target=self.run_analyze, daemon=True).start()

    def start_download_thread(self):
        self.download_button.configure(state="disabled")
        threading.Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        url = self.url_entry.get()
        res = self.res_entry.get().strip() or "1080"
        fps = self.fps_entry.get().strip() or "60"

        ydl_opts = {
            'format': f"bestvideo[height={res}][fps<={fps}]+bestaudio/bestvideo[height={res}]+bestaudio/best",
            'outtmpl': os.path.expanduser('~/Downloads/%(title)s.%(ext)s'),
            'logger': MyLogger(),
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'prefer_ffmpeg': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="Download Finished!", text_color="#00FF00")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#FF0000")
        self.download_button.configure(state="normal")

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()