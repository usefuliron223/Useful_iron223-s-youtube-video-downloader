import customtkinter as ctk
import yt_dlp
import os
import threading
import webbrowser

class MyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Useful_iron223's video Downloader")
        self.geometry("900x850")
        self.minsize(600, 650)
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="USEFUL_IRON223'S DOWNLOADER", font=("Arial", 24, "bold"), text_color="#CC00CC")
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=1, column=0, padx=30, pady=20, sticky="nsew")
        
        for i in range(10):
            self.main_frame.grid_rowconfigure(i, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Paste YouTube URL here", height=45, corner_radius=15)
        self.url_entry.grid(row=0, column=0, padx=30, pady=10, sticky="ew")

        self.analyze_button = ctk.CTkButton(self.main_frame, text="1. ANALYZE LINK", command=self.start_analyze_thread, 
                                           fg_color="#9900CC", hover_color="#770099", height=45, corner_radius=15, font=("Arial", 14, "bold"))
        self.analyze_button.grid(row=1, column=0, padx=30, pady=10, sticky="ew")

        self.mode_var = ctk.StringVar(value="combine")
        self.radio_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.radio_frame.grid(row=2, column=0, pady=10)
        
        self.combine_radio = ctk.CTkRadioButton(self.radio_frame, text="Combine (Video + Audio)", variable=self.mode_var, value="combine", command=self.update_ui_state, fg_color="#CC00CC")
        self.combine_radio.pack(side="left", padx=20)
        
        self.video_radio = ctk.CTkRadioButton(self.radio_frame, text="Video Only", variable=self.mode_var, value="video", command=self.update_ui_state, fg_color="#CC00CC")
        self.video_radio.pack(side="left", padx=20)

        self.audio_radio = ctk.CTkRadioButton(self.radio_frame, text="Audio Only", variable=self.mode_var, value="audio", command=self.update_ui_state, fg_color="#CC00CC")
        self.audio_radio.pack(side="left", padx=20)

        self.results_label = ctk.CTkLabel(self.main_frame, text="Select options below after analysis", text_color="#00FFFF", font=("Arial", 14))
        self.results_label.grid(row=3, column=0, pady=5, sticky="nsew")

        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.settings_frame.grid(row=4, column=0, sticky="nsew", padx=20)
        self.settings_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.fmt_dropdown = ctk.CTkComboBox(self.settings_frame, values=["Format"], height=45, corner_radius=12, width=180)
        self.fmt_dropdown.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.res_dropdown = ctk.CTkComboBox(self.settings_frame, values=["Resolution"], height=45, corner_radius=12, width=180)
        self.res_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.fps_dropdown = ctk.CTkComboBox(self.settings_frame, values=["FPS"], height=45, corner_radius=12, width=180)
        self.fps_dropdown.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.download_button = ctk.CTkButton(self.main_frame, text="2. START DOWNLOAD", command=self.start_download_thread, 
                                            fg_color="#0066CC", hover_color="#0055AA", height=60, corner_radius=15, font=("Arial", 18, "bold"))
        self.download_button.grid(row=5, column=0, padx=30, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", text_color="#00FF00", font=("Arial", 15, "italic"))
        self.status_label.grid(row=6, column=0, pady=5, sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=20, corner_radius=10)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=7, column=0, padx=40, pady=(10, 30), sticky="ew")

        self.credits_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.credits_frame.grid(row=2, column=0, pady=15)
        ctk.CTkLabel(self.credits_frame, text="Credits: ", text_color="#AAAAAA", font=("Arial", 12)).pack(side="left")
        self.credits_link = ctk.CTkLabel(self.credits_frame, text="useful_iron223", text_color="#1F6AA5", font=("Arial", 12, "underline"), cursor="hand2")
        self.credits_link.pack(side="left")
        self.credits_link.bind("<Button-1>", lambda e: webbrowser.open("https://guns.lol/useful_iron223"))

    def update_ui_state(self):
        mode = self.mode_var.get()
        if mode == "audio":
            self.fmt_dropdown.configure(values=["mp3", "m4a", "opus", "wav", "flac"])
            self.fmt_dropdown.set("mp3")
            self.res_dropdown.configure(state="normal")
            self.fps_dropdown.configure(state="disabled")
            self.results_label.configure(text="Select Audio Format and Quality (kbps)")
        else:
            self.res_dropdown.configure(state="normal")
            self.fps_dropdown.configure(state="normal")
            if mode == "video":
                self.fmt_dropdown.configure(values=["mp4", "webm", "mkv", "3gp"])
                self.fmt_dropdown.set("mp4")
                self.results_label.configure(text="Video Only: Choose Resolution and FPS")
            else:
                self.fmt_dropdown.configure(values=["mp4", "mkv", "webm"])
                self.fmt_dropdown.set("mp4")
                self.results_label.configure(text="Combined: Choose Format, Resolution, and FPS")
        
        if self.url_entry.get():
            self.start_analyze_thread()

    def my_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            percentage = d.get('downloaded_bytes', 0) / total
            self.progress_bar.set(percentage)
            speed = d.get('_speed_str', '0B/s').strip().replace('\x1b[0;32m', '').replace('\x1b[0m', '')
            self.status_label.configure(text=f"Downloading: {int(percentage*100)}% | Speed: {speed}")

    def run_analyze(self):
        url = self.url_entry.get()
        if not url: return
        self.status_label.configure(text="Analyzing...", text_color="#FFFF00")
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                if self.mode_var.get() == "audio":
                    audio_bitrates = sorted(set(int(f.get('abr')) for f in formats if f.get('vcodec') == 'none' and f.get('abr')), reverse=True)
                    if audio_bitrates:
                        bitrate_values = [str(b) for b in audio_bitrates]
                        self.res_dropdown.configure(values=bitrate_values)
                        self.res_dropdown.set(bitrate_values[0])
                        self.results_label.configure(text=f"Available Bitrates: {', '.join(bitrate_values[:5])} kbps")
                else:
                    video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
                    res_list = sorted(set(str(f.get('height')) for f in video_formats), key=int, reverse=True)
                    fps_list = sorted(set(str(int(f.get('fps'))) for f in video_formats if f.get('fps')), key=int, reverse=True)
                    
                    self.res_dropdown.configure(values=res_list)
                    self.res_dropdown.set(res_list[0] if res_list else "Resolution")
                    self.fps_dropdown.configure(values=fps_list)
                    self.fps_dropdown.set(fps_list[0] if fps_list else "FPS")
                    
                    if self.mode_var.get() == "combine":
                        available_exts = sorted(set(f.get('ext') for f in video_formats if f.get('ext')), reverse=True)
                        if available_exts:
                            self.fmt_dropdown.configure(values=available_exts)
                            self.fmt_dropdown.set(available_exts[0])
                    
                    self.results_label.configure(text=f"Resolutions: {', '.join(res_list[:5])}p | Max FPS: {fps_list[0] if fps_list else '--'}")
                
                self.status_label.configure(text="Analysis complete.", text_color="#00FF00")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#FF0000")
        self.analyze_button.configure(state="normal")

    def start_analyze_thread(self):
        self.analyze_button.configure(state="disabled")
        threading.Thread(target=self.run_analyze, daemon=True).start()

    def start_download_thread(self):
        self.download_button.configure(state="disabled")
        threading.Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        url = self.url_entry.get()
        fmt = self.fmt_dropdown.get()
        mode = self.mode_var.get()
        val_res = self.res_dropdown.get() 
        val_fps = self.fps_dropdown.get()

        if mode == "combine":
            ydl_opts = {
                'format': f"bestvideo[ext={fmt}][height<={val_res}][fps<={val_fps}]+bestaudio/best",
                'outtmpl': os.path.expanduser('~/Downloads/%(title)s.%(ext)s'),
                'merge_output_format': fmt,
            }
        elif mode == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': fmt,
                    'preferredquality': val_res,
                }],
                'outtmpl': os.path.expanduser('~/Downloads/%(title)s.%(ext)s'),
            }
        else:
            ydl_opts = {
                'format': f"bestvideo[ext={fmt}][height<={val_res}][fps<={val_fps}]",
                'outtmpl': os.path.expanduser('~/Downloads/%(title)s.%(ext)s'),
            }

        ydl_opts['progress_hooks'] = [self.my_hook]
        ydl_opts['quiet'] = True

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
