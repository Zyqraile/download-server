import tkinter as tk
from tkinter import filedialog
import miniaudio
import time
import random
import urllib.request
import os

class SpectrMusicPlayer:
    CURRENT_VERSION = "1.0"
    VERSION_URL = "https://raw.githubusercontent.com/Zyqraile/download-server/main/Spectr%20Music/version.txt"
    EXE_URL = "https://raw.githubusercontent.com/Zyqraile/download-server/main/Spectr%20Music/Spectr-Music.exe"
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"Spectr Music v{self.CURRENT_VERSION}")
        self.root.geometry("300x230")
        self.root.resizable(False, False)
        
        self.file_path = ""
        self.device = None
        self.duration = 0
        self.start_time = 0
        self.is_playing = False
        self.after_id = None
        
        # Kontrola aktualizací při startu
        self.check_for_updates()
        
        # Spektrogram / Vizualizér (Canvas)
        self.canvas = tk.Canvas(root, width=280, height=60, bg="black", highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(padx=10, pady=10)
        
        # UI Elements (Windows Legacy style)
        self.label = tk.Label(root, text="Žádný soubor", relief="sunken", anchor="w", bg="#ffffff", bd=2)
        self.label.pack(fill="x", padx=10, pady=2)
        
        # Časovač (Start / End time)
        self.time_label = tk.Label(root, text="0:00 / 0:00", font=("Courier", 9), fg="#000000")
        self.time_label.pack(pady=2)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.btn_open = tk.Button(btn_frame, text="Otevřít", command=self.load_file, width=7)
        self.btn_open.pack(side="left", padx=2)
        
        self.btn_play = tk.Button(btn_frame, text="Přehrát", command=self.play_audio, width=7)
        self.btn_play.pack(side="left", padx=2)
        
        self.btn_stop = tk.Button(btn_frame, text="Zastavit", command=self.stop_audio, width=7)
        self.btn_stop.pack(side="left", padx=2)
        
        # Spuštění smyčky pro aktualizaci UI na 30 FPS (33 ms)
        self.update_ui_loop()

    def check_for_updates(self):
        try:
            cache_busted_url = f"{self.VERSION_URL}?t={int(time.time())}"
            req = urllib.request.Request(
                cache_busted_url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=8) as response:
                raw_data = response.read()
                remote_version = raw_data.decode('utf-8').strip()
            
            # Výpis verzí do konzole
            print(f"Stažená (lokální) verze: {self.CURRENT_VERSION} | Vzdálená verze: {remote_version}")
            
            if remote_version > self.CURRENT_VERSION:
                print("Nová verze nalezena! Stahuji Spectr-Music.exe...")
                
                save_dir = os.path.join("download", "spectr-music")
                os.makedirs(save_dir, exist_ok=True)
                
                exe_req = urllib.request.Request(
                    self.EXE_URL, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                exe_save_path = os.path.join(save_dir, "Spectr-Music.exe")
                
                with urllib.request.urlopen(exe_req, timeout=15) as resp, open(exe_save_path, 'wb') as f:
                    f.write(resp.read())
                
                print(f"Staženo a uloženo do: {exe_save_path}")
                self.root.title(f"Spectr Music (Nová verze {remote_version} stažena!)")
        except Exception as e:
            print("Kontrola aktualizací selhala (offline režim):", e)

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio soubory", "*.mp3 *.wav *.flac")])
        if self.file_path:
            filename = self.file_path.split("/")[-1].split("\\")[-1]
            self.label.config(text=filename)
            try:
                info = miniaudio.get_file_info(self.file_path)
                self.duration = info.duration
            except:
                self.duration = 0

    def play_audio(self):
        if self.file_path:
            self.stop_audio()
            try:
                stream = miniaudio.stream_file(self.file_path)
                self.device = miniaudio.PlaybackDevice()
                self.device.start(stream)
                self.start_time = time.time()
                self.is_playing = True
            except Exception as e:
                print("Chyba při přehrávání:", e)

    def stop_audio(self):
        if self.device:
            try:
                self.device.stop()
                self.device.close()
            except:
                pass
            self.device = None
        self.is_playing = False
        self.time_label.config(text="0:00 / 0:00")
        self.canvas.delete("all")

    def update_ui_loop(self):
        if self.is_playing and self.duration > 0:
            elapsed = time.time() - self.start_time
            if elapsed >= self.duration:
                self.stop_audio()
            else:
                curr_min, curr_sec = divmod(int(elapsed), 60)
                tot_min, tot_sec = divmod(int(self.duration), 60)
                self.time_label.config(text=f"{curr_min}:{curr_sec:02d} / {tot_min}:{tot_sec:02d}")
                
                self.canvas.delete("all")
                for i in range(20):
                    h = random.randint(8, 55)
                    color = f"#00{random.randint(120,255):02x}{random.randint(80,255):02x}"
                    self.canvas.create_rectangle(i * 14 + 4, 60 - h, i * 14 + 14, 60, fill=color, outline="")
                    
        self.after_id = self.root.after(33, self.update_ui_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectrMusicPlayer(root)
    root.mainloop()