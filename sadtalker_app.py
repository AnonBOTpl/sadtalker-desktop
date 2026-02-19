"""
SadTalker Desktop App v2
Requires: customtkinter, pillow
Run: python sadtalker_app.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading, subprocess, sys, os, json, urllib.request, time
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"
GFPGAN_DIR      = BASE_DIR / "gfpgan" / "weights"
RESULTS_DIR     = BASE_DIR / "results"
SETTINGS_FILE   = BASE_DIR / "app_settings.json"

# ── Models ────────────────────────────────────────────────────────────────────
MODELS = {
    "checkpoints": [
        ("mapping_00109-model.pth.tar",     "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar"),
        ("mapping_00229-model.pth.tar",     "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar"),
        ("SadTalker_V0.0.2_256.safetensors","https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors"),
        ("SadTalker_V0.0.2_512.safetensors","https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors"),
    ],
    "gfpgan": [
        ("alignment_WFLW_4HG.pth",        "https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth"),
        ("detection_Resnet50_Final.pth",   "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth"),
        ("GFPGANv1.4.pth",                "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth"),
        ("parsing_parsenet.pth",           "https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth"),
    ]
}

# ── i18n ──────────────────────────────────────────────────────────────────────
LANG = {
    "en": {
        "app_title": "SadTalker Desktop",
        "tab_generate": "🎬  Generate",
        "tab_settings": "⚙️  Settings",
        "tab_setup":    "🔧  Setup",
        "tab_about":    "ℹ️  About",
        # Generate tab
        "gen_title":       "🎬  Generate video",
        "gen_image_lbl":   "📷  Photo / photos:",
        "gen_image_btn":   "Choose images",
        "gen_audio_lbl":   "🎵  Audio file:",
        "gen_audio_btn":   "Choose audio",
        "gen_none":        "Not selected",
        "gen_btn":         "▶  Generate video",
        "gen_open":        "📂  Open results folder",
        "gen_running":     "⏳  Generating…",
        "gen_ready":       "Ready.",
        "gen_done":        "✅  Done! Generated {n} video(s).",
        "gen_warn_img":    "Select at least one image!",
        "gen_warn_audio":  "Select an audio file!",
        "gen_warn_setup":  "Run Setup first (🔧 Setup tab) to install dependencies and download models!",
        "gen_log_batch":   "── [{i}/{n}] {name} ──",
        "gen_log_done":    "✅  All done. Results in: {path}",
        "gen_err":         "❌  Error (code {code})",
        "gen_ok":          "✅  Success!",
        # Settings tab
        "set_title":       "⚙️  Generation settings",
        "set_save":        "💾  Save settings",
        "set_saved":       "Settings saved!",
        "set_size_lbl":    "📐  Output size",
        "set_size_tip":    "Resolution of the generated face.\n256 = faster, less VRAM (recommended for GTX 1060 6 GB).\n512 = better quality, needs ~4 GB VRAM.\nIf you get CUDA out-of-memory errors, switch to 256.",
        "set_enh_lbl":     "✨  Face enhancer",
        "set_enh_tip":     "Post-processing to improve face quality.\ngfpgan – recommended, best results.\nrestoreformer – alternative, slightly different style.\nnone – no enhancer, fastest, lower quality.",
        "set_pre_lbl":     "🔲  Preprocess mode",
        "set_pre_tip":     "How the input image is prepared before generation.\ncrop – auto-detects and crops the face region (recommended for portraits).\nresize – scales the whole image to the target size.\nfull – uses the full image without any cropping.",
        "set_still_lbl":   "🧍  Still mode",
        "set_still_tip":   "When ON, head movement is minimized — only lip movement is generated.\nIdeal for presentations, explainer videos, or formal content.\nWhen OFF, natural head movement is added.",
        "set_still_sw":    "Enable still mode",
        "set_exp_lbl":     "😮  Expression scale",
        "set_exp_tip":     "Controls the intensity of facial expressions.\n1.0 = natural (default).\n< 1.0 = subtler, more neutral expressions.\n> 1.0 = exaggerated expressions (max 2.0).\nStart with 1.0 and adjust to taste.",
        "set_pose_lbl":    "🎭  Pose style",
        "set_pose_tip":    "Selects the head movement animation style (0–45).\n0 = default neutral style.\nHigher values introduce different rhythmic head motions.\nExperiment to find what matches your audio best.",
        # Setup tab
        "setup_title":     "🔧  Auto-installer",
        "setup_desc":      "Checks and installs all required dependencies, then downloads AI models.\nRun once on first use or after any import errors.",
        "setup_full":      "▶  Run full setup",
        "setup_pip":       "📦  Packages only",
        "setup_models":    "⬇️  Models only",
        "setup_status":    "Installation log:",
        "setup_checking":  "Checking pip dependencies…",
        "setup_installed": "✓ {pkg} already installed",
        "setup_installing":"⬇️  Installing {pkg}…",
        "setup_ok":        "✅  {pkg} installed",
        "setup_err":       "❌  Error with {pkg}: {err}",
        "setup_pkgs_done": "📦  Dependencies ready.",
        "setup_models_chk":"⬇️  Checking models…",
        "setup_mdl_exists":"✓ {f} already exists",
        "setup_mdl_dl":    "⬇️  Downloading {f}…",
        "setup_mdl_ok":    "✅  {f} downloaded",
        "setup_mdl_err":   "❌  Download error {f}: {e}",
        "setup_mdl_link":  "   Manual link: {url}",
        "setup_mdl_done":  "⬇️  Models ready.",
        "setup_all_done":  "\n✅  Full setup complete!",
        # About
        "about_text": (
            "SadTalker Desktop  v2.0\n\n"
            "A desktop GUI for the SadTalker talking-head synthesis model.\n\n"
            "Original SadTalker paper:\nZhang et al., 2023 — OpenTalker/SadTalker on GitHub\n\n"
            "GPU detected: {gpu}\nCUDA version: {cuda}\nVRAM: {vram}"
        ),
        # Header GPU info
        "gpu_detecting":   "Detecting GPU…",
        "gpu_unknown":     "GPU: unknown",
    },
    "pl": {
        "app_title": "SadTalker Desktop",
        "tab_generate": "🎬  Generuj",
        "tab_settings": "⚙️  Ustawienia",
        "tab_setup":    "🔧  Setup",
        "tab_about":    "ℹ️  O aplikacji",
        # Generate tab
        "gen_title":       "🎬  Generowanie wideo",
        "gen_image_lbl":   "📷  Zdjęcie / zdjęcia:",
        "gen_image_btn":   "Wybierz zdjęcia",
        "gen_audio_lbl":   "🎵  Plik audio:",
        "gen_audio_btn":   "Wybierz audio",
        "gen_none":        "Nie wybrano",
        "gen_btn":         "▶  Generuj wideo",
        "gen_open":        "📂  Otwórz folder results",
        "gen_running":     "⏳  Generuję…",
        "gen_ready":       "Gotowy.",
        "gen_done":        "✅  Gotowe! Wygenerowano {n} wideo.",
        "gen_warn_img":    "Wybierz co najmniej jedno zdjęcie!",
        "gen_warn_audio":  "Wybierz plik audio!",
        "gen_warn_setup":  "Najpierw uruchom Setup (zakładka 🔧 Setup) — zainstaluje zależności i pobierze modele!",
        "gen_log_batch":   "── [{i}/{n}] {name} ──",
        "gen_log_done":    "✅  Wszystko gotowe. Wyniki w: {path}",
        "gen_err":         "❌  Błąd (kod {code})",
        "gen_ok":          "✅  Sukces!",
        # Settings tab
        "set_title":       "⚙️  Ustawienia generowania",
        "set_save":        "💾  Zapisz ustawienia",
        "set_saved":       "Ustawienia zapisane!",
        "set_size_lbl":    "📐  Rozmiar wyjściowy",
        "set_size_tip":    "Rozdzielczość generowanej twarzy.\n256 = szybciej, mniej VRAM (zalecane dla GTX 1060 6 GB).\n512 = lepsza jakość, wymaga ~4 GB VRAM.\nJeśli pojawia się błąd CUDA out-of-memory, przełącz na 256.",
        "set_enh_lbl":     "✨  Enhancer twarzy",
        "set_enh_tip":     "Post-processing poprawiający jakość twarzy.\ngfpgan – zalecany, najlepsze wyniki.\nrestoreformer – alternatywa, nieco inny styl.\nnone – bez enhancera, najszybciej, niższa jakość.",
        "set_pre_lbl":     "🔲  Tryb preprocessingu",
        "set_pre_tip":     "Sposób przygotowania obrazu przed generowaniem.\ncrop – automatycznie wykrywa i wycina twarz (zalecane dla portretów).\nresize – skaluje cały obraz do docelowego rozmiaru.\nfull – używa pełnego obrazu bez kadrowania.",
        "set_still_lbl":   "🧍  Still mode",
        "set_still_tip":   "Gdy WŁĄCZONY, ruch głowy jest zminimalizowany — animowane są tylko usta.\nIdealny do prezentacji, filmów instruktażowych lub formalnych treści.\nGdy WYŁĄCZONY, dodawany jest naturalny ruch głowy.",
        "set_still_sw":    "Włącz still mode",
        "set_exp_lbl":     "😮  Expression scale",
        "set_exp_tip":     "Kontroluje intensywność mimiki twarzy.\n1.0 = naturalna (domyślna).\n< 1.0 = subtelniejsza, bardziej neutralna mimika.\n> 1.0 = wyolbrzymiona mimika (maks. 2.0).\nZacznij od 1.0 i dostosuj do potrzeb.",
        "set_pose_lbl":    "🎭  Pose style",
        "set_pose_tip":    "Wybiera styl animacji ruchu głowy (0–45).\n0 = domyślny neutralny styl.\nWyższe wartości wprowadzają różne rytmiczne ruchy głowy.\nEksperymentuj, aby dobrać styl do audio.",
        # Setup tab
        "setup_title":     "🔧  Auto-installer",
        "setup_desc":      "Sprawdza i instaluje wszystkie wymagane zależności oraz pobiera modele AI.\nUruchom raz przy pierwszej konfiguracji lub po błędach importu.",
        "setup_full":      "▶  Uruchom pełny setup",
        "setup_pip":       "📦  Tylko paczki pip",
        "setup_models":    "⬇️  Tylko modele",
        "setup_status":    "Log instalacji:",
        "setup_checking":  "Sprawdzam zależności pip…",
        "setup_installed": "✓ {pkg} już zainstalowany",
        "setup_installing":"⬇️  Instaluję {pkg}…",
        "setup_ok":        "✅  {pkg} zainstalowany",
        "setup_err":       "❌  Błąd przy {pkg}: {err}",
        "setup_pkgs_done": "📦  Zależności gotowe.",
        "setup_models_chk":"⬇️  Sprawdzam modele…",
        "setup_mdl_exists":"✓ {f} już istnieje",
        "setup_mdl_dl":    "⬇️  Pobieranie {f}…",
        "setup_mdl_ok":    "✅  {f} pobrano",
        "setup_mdl_err":   "❌  Błąd pobierania {f}: {e}",
        "setup_mdl_link":  "   Ręczny link: {url}",
        "setup_mdl_done":  "⬇️  Modele gotowe.",
        "setup_all_done":  "\n✅  Pełny setup zakończony!",
        # About
        "about_text": (
            "SadTalker Desktop  v2.0\n\n"
            "Desktopowy interfejs dla modelu syntezy mowy SadTalker.\n\n"
            "Oryginalny artykuł SadTalker:\nZhang et al., 2023 — OpenTalker/SadTalker na GitHub\n\n"
            "Wykryta karta GPU: {gpu}\nWersja CUDA: {cuda}\nVRAM: {vram}"
        ),
        "gpu_detecting":   "Wykrywanie GPU…",
        "gpu_unknown":     "GPU: nieznany",
    }
}

DEFAULT_SETTINGS = {
    "size": "256", "enhancer": "gfpgan", "preprocess": "crop",
    "still": False, "expression_scale": 1.0, "pose_style": 0,
    "theme": "dark", "lang": "en",
}

def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def detect_gpu():
    """Returns (name, cuda_ver, vram_mb) or None."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
             "--format=csv,noheader,nounits"],
            text=True, timeout=5
        ).strip().splitlines()[0]
        parts = [p.strip() for p in out.split(",")]
        name, driver, vram = parts[0], parts[1], int(parts[2])
        # get CUDA version from nvidia-smi header line
        smi = subprocess.check_output(["nvidia-smi"], text=True, timeout=5)
        cuda = "?"
        for tok in smi.split():
            if tok.startswith("CUDA") or tok.replace(".","").isdigit():
                pass
        import re
        m = re.search(r"CUDA Version:\s*([\d.]+)", smi)
        cuda = m.group(1) if m else driver
        return name, cuda, vram
    except Exception:
        return None


# ── Tooltip ───────────────────────────────────────────────────────────────────
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)
        widget.bind("<ButtonPress>", self._hide)

    def _show(self, _=None):
        if not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        self.tw.attributes("-topmost", True)
        frm = tk.Frame(self.tw, background="#1c1c2e", bd=1, relief="solid",
                       highlightbackground="#4a4a6a", highlightthickness=1)
        frm.pack()
        tk.Label(frm, text=self.text, background="#1c1c2e", foreground="#e0e0f0",
                 font=("Segoe UI", 10), justify="left", padx=10, pady=7,
                 wraplength=340).pack()

    def _hide(self, _=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None


def labeled_row(parent, lbl_text, tip_text, row, widget_factory):
    """Renders a label + ⓘ icon row and attaches tooltip, then calls widget_factory for the control."""
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.grid(row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 2))

    lbl = ctk.CTkLabel(f, text=lbl_text, font=("Segoe UI", 13, "bold"))
    lbl.pack(side="left")

    info = ctk.CTkLabel(f, text=" ⓘ", font=("Segoe UI", 13), text_color="#6a9fe0", cursor="question_arrow")
    info.pack(side="left", padx=(4, 0))
    Tooltip(info, tip_text)

    ctrl_frame = ctk.CTkFrame(parent, fg_color="transparent")
    ctrl_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=22, pady=(0, 4))
    widget_factory(ctrl_frame)
    return ctrl_frame


# ══════════════════════════════════════════════════════════════════════════════
class SetupTab(ctk.CTkFrame):
    def __init__(self, parent, t, log_cb):
        super().__init__(parent, fg_color="transparent")
        self.t = t
        self.log_cb = log_cb
        self._build()

    def refresh(self, t):
        self.t = t
        for w in self.winfo_children(): w.destroy()
        self._build()

    def _build(self):
        t = self.t
        ctk.CTkLabel(self, text=t["setup_title"], font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0,6))
        ctk.CTkLabel(self, text=t["setup_desc"], wraplength=660, justify="left",
                     font=("Segoe UI", 11), text_color="gray70").pack(anchor="w", pady=(0,12))

        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(anchor="w", pady=(0,10))
        ctk.CTkButton(bf, text=t["setup_full"],   command=self._full,   width=210, height=40).pack(side="left", padx=(0,8))
        ctk.CTkButton(bf, text=t["setup_pip"],    command=self._pip,    width=180, height=40,
                      fg_color="#2d6a2d", hover_color="#3a8a3a").pack(side="left", padx=(0,8))
        ctk.CTkButton(bf, text=t["setup_models"], command=self._models, width=180, height=40,
                      fg_color="#2d4a6a", hover_color="#3a6090").pack(side="left")

        ctk.CTkLabel(self, text=t["setup_status"], font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8,2))
        self.box = ctk.CTkTextbox(self, height=300, font=("Consolas", 11))
        self.box.pack(fill="both", expand=True)

    def log(self, msg):
        self.box.configure(state="normal")
        self.box.insert("end", msg + "\n")
        self.box.see("end")
        self.box.configure(state="disabled")
        self.log_cb(msg)

    def _full(self):   threading.Thread(target=self._do_full,   daemon=True).start()
    def _pip(self):    threading.Thread(target=self._do_pip,    daemon=True).start()
    def _models(self): threading.Thread(target=self._do_models, daemon=True).start()

    def _do_full(self):
        self._do_pip()
        self._do_models()
        self.log(self.t["setup_all_done"])

    def _do_pip(self):
        t = self.t
        self.log("═"*50 + "\n" + t["setup_checking"])
        pkgs = [
            ("setuptools<70",  "pkg_resources"),
            ("cmake",           None),
            ("dlib",            "dlib"),
            ("librosa==0.9.2",  "librosa"),
            ("gfpgan",          "gfpgan"),
            ("basicsr",         "basicsr"),
            ("facexlib",        "facexlib"),
            ("gradio==3.41.2",  "gradio"),
            ("pillow",          "PIL"),
        ]
        for pkg, mod in pkgs:
            short = pkg.split("==")[0].split("<")[0]
            if mod:
                try:
                    __import__(mod)
                    self.log(t["setup_installed"].format(pkg=short))
                    continue
                except ImportError:
                    pass
            self.log(t["setup_installing"].format(pkg=pkg))
            r = subprocess.run([sys.executable, "-m", "pip", "install", pkg],
                               capture_output=True, text=True)
            if r.returncode == 0:
                self.log(t["setup_ok"].format(pkg=short))
            else:
                self.log(t["setup_err"].format(pkg=short, err=r.stderr[-200:]))
        self.log(t["setup_pkgs_done"])

    def _do_models(self):
        t = self.t
        self.log("═"*50 + "\n" + t["setup_models_chk"])
        CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
        GFPGAN_DIR.mkdir(parents=True, exist_ok=True)
        dirs = {"checkpoints": CHECKPOINTS_DIR, "gfpgan": GFPGAN_DIR}
        for grp, items in MODELS.items():
            for fname, url in items:
                dest = dirs[grp] / fname
                if dest.exists():
                    self.log(t["setup_mdl_exists"].format(f=fname))
                    continue
                self.log(t["setup_mdl_dl"].format(f=fname))
                try:
                    urllib.request.urlretrieve(url, dest)
                    self.log(t["setup_mdl_ok"].format(f=fname))
                except Exception as e:
                    self.log(t["setup_mdl_err"].format(f=fname, e=e))
                    self.log(t["setup_mdl_link"].format(url=url))
        self.log(t["setup_mdl_done"])


# ══════════════════════════════════════════════════════════════════════════════
class GenerateTab(ctk.CTkFrame):
    def __init__(self, parent, settings, t, log_cb):
        super().__init__(parent, fg_color="transparent")
        self.settings  = settings
        self.t         = t
        self.log_cb    = log_cb
        self.img_paths = []
        self.audio_var = tk.StringVar()
        self.running   = False
        self._build()

    def _build(self):
        t = self.t
        ctk.CTkLabel(self, text=t["gen_title"], font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0,8))

        inp = ctk.CTkFrame(self, corner_radius=10)
        inp.pack(fill="x", pady=(0,10))
        inp.columnconfigure(1, weight=1)

        # Image row
        ctk.CTkLabel(inp, text=t["gen_image_lbl"], font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12,4))
        self.img_lbl = ctk.CTkLabel(inp, text=t["gen_none"], text_color="gray60", anchor="w")
        self.img_lbl.grid(row=0, column=1, sticky="ew", padx=8)
        ctk.CTkButton(inp, text=t["gen_image_btn"], width=155, command=self._pick_img).grid(
            row=0, column=2, padx=14, pady=(12,4))

        # Audio row
        ctk.CTkLabel(inp, text=t["gen_audio_lbl"], font=("Segoe UI", 13, "bold")).grid(
            row=1, column=0, sticky="w", padx=14, pady=(4,12))
        self.audio_lbl = ctk.CTkLabel(inp, text=t["gen_none"], text_color="gray60", anchor="w")
        self.audio_lbl.grid(row=1, column=1, sticky="ew", padx=8)
        ctk.CTkButton(inp, text=t["gen_audio_btn"], width=155, command=self._pick_audio).grid(
            row=1, column=2, padx=14, pady=(4,12))

        # Buttons
        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(fill="x", pady=(0,8))
        self.gen_btn = ctk.CTkButton(bf, text=t["gen_btn"], height=44,
                                     font=("Segoe UI", 14, "bold"), command=self._start)
        self.gen_btn.pack(side="left", fill="x", expand=True, padx=(0,8))
        ctk.CTkButton(bf, text=t["gen_open"], width=200, height=44,
                      fg_color="#444", hover_color="#555",
                      command=lambda: os.startfile(RESULTS_DIR) if RESULTS_DIR.exists() else None
                      ).pack(side="left")

        # Progress
        self.prog = ctk.CTkProgressBar(self, height=12)
        self.prog.set(0)
        self.prog.pack(fill="x", pady=(0,4))
        self.status_lbl = ctk.CTkLabel(self, text=t["gen_ready"], anchor="w", text_color="gray70",
                                        font=("Segoe UI", 11))
        self.status_lbl.pack(anchor="w")

        # Log
        ctk.CTkLabel(self, text="Log:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8,2))
        self.logbox = ctk.CTkTextbox(self, height=200, font=("Consolas", 10))
        self.logbox.pack(fill="both", expand=True)

    def _pick_img(self):
        p = filedialog.askopenfilenames(title="Images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if p:
            self.img_paths = list(p)
            names = ", ".join(Path(x).name for x in p)
            self.img_lbl.configure(text=(names[:80]+"…" if len(names)>80 else names), text_color="white")

    def _pick_audio(self):
        p = filedialog.askopenfilename(title="Audio",
            filetypes=[("Audio", "*.wav *.mp3 *.ogg *.flac")])
        if p:
            self.audio_var.set(p)
            self.audio_lbl.configure(text=Path(p).name, text_color="white")

    def _log(self, msg):
        self.logbox.configure(state="normal")
        self.logbox.insert("end", msg+"\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")
        self.log_cb(msg)

    def _status(self, msg, p=None):
        self.status_lbl.configure(text=msg)
        if p is not None: self.prog.set(p)

    def _start(self):
        t = self.t
        if self.running: return
        if not self.img_paths:
            messagebox.showwarning("!", t["gen_warn_img"]); return
        if not self.audio_var.get():
            messagebox.showwarning("!", t["gen_warn_audio"]); return
        if not CHECKPOINTS_DIR.exists() or not any(CHECKPOINTS_DIR.iterdir()):
            messagebox.showwarning("!", t["gen_warn_setup"]); return
        threading.Thread(target=self._batch, daemon=True).start()

    def _batch(self):
        t  = self.t
        self.running = True
        self.gen_btn.configure(state="disabled", text=t["gen_running"])
        n  = len(self.img_paths)
        for i, img in enumerate(self.img_paths, 1):
            self._status(f"{t['gen_running']} {i}/{n}", (i-1)/n)
            self._log("\n" + t["gen_log_batch"].format(i=i, n=n, name=Path(img).name))
            self._run(img)
            self.prog.set(i/n)
        self._status(t["gen_done"].format(n=n), 1.0)
        self._log(t["gen_log_done"].format(path=RESULTS_DIR))
        self.running = False
        self.gen_btn.configure(state="normal", text=t["gen_btn"])
        if RESULTS_DIR.exists(): os.startfile(RESULTS_DIR)

    def _run(self, img):
        t, s = self.t, self.settings
        RESULTS_DIR.mkdir(exist_ok=True)
        cmd = [
            sys.executable, str(BASE_DIR / "inference.py"),
            "--driven_audio", self.audio_var.get(),
            "--source_image", img,
            "--result_dir",   str(RESULTS_DIR),
            "--size",         s["size"],
            "--expression_scale", str(s["expression_scale"]),
            "--pose_style",   str(int(s["pose_style"])),
            "--preprocess",   s["preprocess"],
        ]
        if s["enhancer"] != "none": cmd += ["--enhancer", s["enhancer"]]
        if s["still"]:              cmd += ["--still"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, cwd=str(BASE_DIR),
                                env={**os.environ, "PYTHONUNBUFFERED": "1"})
        for line in proc.stdout:
            line = line.rstrip()
            if line: self._log(line)
        proc.wait()
        self._log(t["gen_err"].format(code=proc.returncode) if proc.returncode != 0 else t["gen_ok"])


# ══════════════════════════════════════════════════════════════════════════════
class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent, settings, t, on_save):
        super().__init__(parent, fg_color="transparent")
        self.settings = settings
        self.t        = t
        self.on_save  = on_save
        self._vars    = {}
        self._build()

    def refresh(self, t):
        self.t = t
        for w in self.winfo_children(): w.destroy()
        self._vars = {}
        self._build()

    def _build(self):
        t, s = self.t, self.settings
        ctk.CTkLabel(self, text=t["set_title"], font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0,8))

        frm = ctk.CTkFrame(self, corner_radius=10)
        frm.pack(fill="x", pady=(0,10))
        frm.columnconfigure(0, weight=1)

        row = 0
        def next_rows():
            nonlocal row; r = row; row += 2; return r

        # Size
        r = next_rows()
        labeled_row(frm, t["set_size_lbl"], t["set_size_tip"], r,
            lambda f: ctk.CTkSegmentedButton(f, values=["256","512"],
                variable=self._mk("size", tk.StringVar, s["size"])).pack(side="left"))

        # Enhancer
        r = next_rows()
        labeled_row(frm, t["set_enh_lbl"], t["set_enh_tip"], r,
            lambda f: ctk.CTkSegmentedButton(f, values=["gfpgan","restoreformer","none"],
                variable=self._mk("enhancer", tk.StringVar, s["enhancer"])).pack(side="left"))

        # Preprocess
        r = next_rows()
        labeled_row(frm, t["set_pre_lbl"], t["set_pre_tip"], r,
            lambda f: ctk.CTkSegmentedButton(f, values=["crop","resize","full"],
                variable=self._mk("preprocess", tk.StringVar, s["preprocess"])).pack(side="left"))

        # Still mode
        r = next_rows()
        labeled_row(frm, t["set_still_lbl"], t["set_still_tip"], r,
            lambda f: ctk.CTkSwitch(f, text=t["set_still_sw"],
                variable=self._mk("still", tk.BooleanVar, s["still"])).pack(side="left"))

        # Expression scale
        r = next_rows()
        exp_var = self._mk("expression_scale", tk.DoubleVar, s["expression_scale"])
        def _exp_ctrl(f):
            lbl = ctk.CTkLabel(f, text=f"{exp_var.get():.1f}", width=36, font=("Segoe UI", 12))
            lbl.pack(side="right")
            ctk.CTkSlider(f, from_=0.5, to=2.0, number_of_steps=15, variable=exp_var, width=220,
                command=lambda v: lbl.configure(text=f"{v:.1f}")).pack(side="left")
        labeled_row(frm, t["set_exp_lbl"], t["set_exp_tip"], r, _exp_ctrl)

        # Pose style
        r = next_rows()
        pose_var = self._mk("pose_style", tk.IntVar, int(s["pose_style"]))
        def _pose_ctrl(f):
            lbl = ctk.CTkLabel(f, text=str(pose_var.get()), width=30, font=("Segoe UI", 12))
            lbl.pack(side="right")
            ctk.CTkSlider(f, from_=0, to=45, number_of_steps=45, variable=pose_var, width=220,
                command=lambda v: lbl.configure(text=str(int(v)))).pack(side="left")
        labeled_row(frm, t["set_pose_lbl"], t["set_pose_tip"], r, _pose_ctrl)

        # Language + theme row
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", pady=(4,0))

        ctk.CTkLabel(bot, text="🌐  Language / Język:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0,8))
        lang_var = self._mk("lang", tk.StringVar, s.get("lang","en"))
        ctk.CTkSegmentedButton(bot, values=["en","pl"], variable=lang_var, width=110).pack(side="left", padx=(0,20))

        ctk.CTkLabel(bot, text="🎨  Theme:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0,8))
        theme_var = self._mk("theme", tk.StringVar, s.get("theme","dark"))
        ctk.CTkSegmentedButton(bot, values=["dark","light","system"], variable=theme_var, width=180).pack(side="left")

        ctk.CTkButton(self, text=t["set_save"], height=40, command=self._save).pack(anchor="w", pady=12)

    def _mk(self, key, cls, val):
        v = cls(value=val)
        self._vars[key] = v
        return v

    def _save(self):
        for k, v in self._vars.items():
            val = v.get()
            if k == "pose_style": val = int(val)
            self.settings[k] = val
        save_settings(self.settings)
        ctk.set_appearance_mode(self.settings.get("theme","dark"))
        self.on_save()
        messagebox.showinfo("✅", self.t["set_saved"])


# ══════════════════════════════════════════════════════════════════════════════
class AboutTab(ctk.CTkFrame):
    def __init__(self, parent, t, gpu_info):
        super().__init__(parent, fg_color="transparent")
        self.t = t
        self.gpu_info = gpu_info
        self._build()

    def refresh(self, t, gpu_info):
        self.t = t; self.gpu_info = gpu_info
        for w in self.winfo_children(): w.destroy()
        self._build()

    def _build(self):
        t = self.t
        gi = self.gpu_info
        if gi:
            gpu_str  = gi[0]
            cuda_str = gi[1]
            vram_str = f"{gi[2]} MB ({gi[2]//1024:.1f} GB)"
        else:
            gpu_str = cuda_str = vram_str = "N/A"

        ctk.CTkLabel(self, text=t["tab_about"].replace("ℹ️  ",""),
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0,12))

        box = ctk.CTkFrame(self, corner_radius=12)
        box.pack(fill="x")
        ctk.CTkLabel(box,
            text=t["about_text"].format(gpu=gpu_str, cuda=cuda_str, vram=vram_str),
            font=("Segoe UI", 12), justify="left", anchor="w",
            wraplength=640).pack(padx=20, pady=16, anchor="w")

        ctk.CTkButton(self, text="🔗  GitHub — OpenTalker/SadTalker", width=260, height=36,
                      fg_color="#2d4a6a", hover_color="#3a6090",
                      command=lambda: os.startfile("https://github.com/OpenTalker/SadTalker")
                      ).pack(anchor="w", pady=(12,0))


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        ctk.set_appearance_mode(self.settings.get("theme","dark"))
        ctk.set_default_color_theme("blue")
        self.title("SadTalker Desktop")
        self.geometry("820x720")
        self.minsize(740, 600)

        self.gpu_info = None
        self._build_header()
        self._build_tabs()
        threading.Thread(target=self._detect_gpu_async, daemon=True).start()

    @property
    def t(self):
        return LANG[self.settings.get("lang","en")]

    def _build_header(self):
        self.header = ctk.CTkFrame(self, height=54, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkLabel(self.header, text="  🎭  SadTalker Desktop",
                     font=("Segoe UI", 17, "bold")).pack(side="left", padx=16, pady=10)
        self.gpu_lbl = ctk.CTkLabel(self.header, text=self.t["gpu_detecting"],
                                     font=("Segoe UI", 11), text_color="gray60")
        self.gpu_lbl.pack(side="right", padx=16)

    def _detect_gpu_async(self):
        info = detect_gpu()
        self.gpu_info = info
        if info:
            txt = f"{info[0]}  •  CUDA {info[1]}  •  {info[2]} MB VRAM"
        else:
            txt = self.t["gpu_unknown"]
        self.after(0, lambda: self.gpu_lbl.configure(text=txt))

    def _build_tabs(self):
        t = self.t
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=10)
        for name in [t["tab_generate"], t["tab_settings"], t["tab_setup"], t["tab_about"]]:
            self.tabview.add(name)

        self.gen_tab   = GenerateTab(self.tabview.tab(t["tab_generate"]), self.settings, t, self._statusbar_log)
        self.gen_tab.pack(fill="both", expand=True)

        self.set_tab   = SettingsTab(self.tabview.tab(t["tab_settings"]), self.settings, t, self._on_settings_save)
        self.set_tab.pack(fill="both", expand=True)

        self.setup_tab = SetupTab(self.tabview.tab(t["tab_setup"]), t, self._statusbar_log)
        self.setup_tab.pack(fill="both", expand=True)

        self.about_tab = AboutTab(self.tabview.tab(t["tab_about"]), t, self.gpu_info)
        self.about_tab.pack(fill="both", expand=True)

        # Statusbar
        self.status_lbl = ctk.CTkLabel(self, text="", anchor="w",
                                        font=("Segoe UI", 10), text_color="gray55")
        self.status_lbl.pack(fill="x", padx=14, pady=(0,5))

    def _statusbar_log(self, msg):
        short = msg[-95:] if len(msg) > 95 else msg
        self.after(0, lambda: self.status_lbl.configure(text=short))

    def _on_settings_save(self):
        t = self.t
        # Rename tabs to new language
        old_names = list(self.tabview._tab_dict.keys())
        new_names = [t["tab_generate"], t["tab_settings"], t["tab_setup"], t["tab_about"]]
        for old, new in zip(old_names, new_names):
            if old != new:
                self.tabview.rename(old, new)
        # Refresh content of each tab in-place
        self.gen_tab.t = t
        for w in self.tabview.tab(t["tab_generate"]).winfo_children():
            w.destroy()
        self.gen_tab = GenerateTab(self.tabview.tab(t["tab_generate"]), self.settings, t, self._statusbar_log)
        self.gen_tab.pack(fill="both", expand=True)

        self.set_tab.refresh(t)

        self.setup_tab.refresh(t)

        self.about_tab.refresh(t, self.gpu_info)


if __name__ == "__main__":
    app = App()
    app.mainloop()