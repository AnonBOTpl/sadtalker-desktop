# 🎭 SadTalker Desktop

A clean, modern desktop GUI for [SadTalker](https://github.com/OpenTalker/SadTalker) — the AI talking-head video generator. Includes a one-click Windows installer that sets up everything automatically.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![GPU](https://img.shields.io/badge/GPU-NVIDIA%20CUDA-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

<img width="815" height="754" alt="screen1" src="https://github.com/user-attachments/assets/ad450622-df20-4e05-95e6-1039ecbcf098" />

---

## ✨ Features

- **One-click installer** — installs Git, Python 3.9, uv, PyTorch (CUDA auto-select), all dependencies, and creates a desktop shortcut
- **Modern GUI** built with CustomTkinter — no browser or terminal required after setup
- **Batch processing** — drop multiple images and generate videos for all of them at once
- **Live generation log** — see exactly what's happening during generation
- **Persistent settings** — size, enhancer, preprocess mode, expression scale, pose style saved between sessions
- **Bilingual interface** — English / Polish (switchable in Settings)
- **Built-in Setup tab** — download AI models and fix missing dependencies from inside the app

---

## 🖥️ Requirements

- Windows 10 / 11 (64-bit)
- NVIDIA GPU with CUDA support (GTX 10xx or newer recommended)
- ~10 GB free disk space (models + dependencies)
- Internet connection for installation

> CPU-only mode is supported but generation will be very slow.

---

## 🚀 Installation

### Step 1 — Download the installer package

Download the latest release from the [Releases](../../releases) page and extract the ZIP. You should have these 3 files in one folder:

```
📁 SadTalker-Desktop/
├── install.bat
├── install.ps1
└── sadtalker_app.py
```

### Step 2 — Run the installer

Double-click **`install.bat`**

> If Windows shows a SmartScreen warning, click **"More info" → "Run anyway"**.  
> The installer does not require Administrator privileges.

The installer will automatically:
- Install Git (if missing)
- Clone the SadTalker repository
- Install Python 3.9 (if missing)
- Install `uv` package manager
- Create an isolated `.venv` virtual environment
- Ask you to select your CUDA version and install the correct PyTorch build
- Install all required Python packages
- Generate an app icon and create a **desktop shortcut**

### Step 3 — Download AI models

On first launch, open the **🔧 Setup** tab and click **"▶ Run full setup"** to download the AI models (~2 GB). Without this step the app cannot generate video.

### Step 4 — Generate your first video

1. Go to the **🎬 Generate** tab
2. Select a portrait photo (PNG or JPG)
3. Select an audio file (WAV or MP3)
4. Click **▶ Generate video**
5. The result will open automatically in your `results/` folder

---

## ⚙️ Settings

| Option | Description |
|---|---|
| **Size** | `256` = faster, less VRAM (recommended for 6 GB cards) / `512` = better quality |
| **Enhancer** | `gfpgan` = best face quality / `restoreformer` = alternative / `none` = fastest |
| **Preprocess** | `crop` = auto-detect face (recommended) / `resize` / `full` |
| **Still mode** | Minimizes head movement — only lips animate. Good for presentations |
| **Expression scale** | `1.0` = natural / `<1.0` = subtle / `>1.0` = exaggerated (max 2.0) |
| **Pose style** | 0–45: different head movement animation styles |

---

## 🗂️ Project structure

```
your-repo/
├── install.bat          # Installer entry point (user double-clicks this)
├── install.ps1          # Main installer logic (PowerShell)
├── sadtalker_app.py     # Desktop GUI application
└── README.md
```

After installation, the SadTalker repo is cloned into a `SadTalker/` subfolder next to the installer files. The app and all dependencies live inside `SadTalker/.venv/` — nothing is installed system-wide.

---

## 🧯 Troubleshooting

**App won't start after installation**  
Make sure `sadtalker_app.py` was in the same folder as `install.bat` during installation. If not, copy it manually to the `SadTalker/` subfolder.

**`No module named 'pkg_resources'`**  
Open the **🔧 Setup** tab and run "Packages only" — it will reinstall `setuptools<70`.

**CUDA not detected / wrong PyTorch version**  
Run `nvidia-smi` in CMD to check your CUDA version, then reinstall PyTorch:  
`.venv\Scripts\activate` → `uv pip install torch==2.1.0+cu121 ... `

**Out of memory (OOM) during generation**  
Switch to **Size 256** in Settings and disable the enhancer (`none`).

**Generation completes but no video in UI**  
This is a known Gradio/SadTalker quirk — the video is always saved to the `results/` folder. Click **📂 Open results folder** to find it.

---

## 📋 Tested configuration

| Component | Version |
|---|---|
| OS | Windows 11 |
| GPU | NVIDIA GeForce GTX 1060 6 GB |
| CUDA | 13.0 (driver 581.80) |
| PyTorch | 2.1.0+cu121 |
| Python | 3.9.13 |

---

## 🙏 Credits

- [SadTalker](https://github.com/OpenTalker/SadTalker) by OpenTalker — Zhang et al., CVPR 2023
- [GFPGAN](https://github.com/TencentARC/GFPGAN) by TencentARC
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky

---

## 📄 License

This project (the installer and GUI) is released under the [MIT License](LICENSE).  
SadTalker itself is subject to its own [license](https://github.com/OpenTalker/SadTalker/blob/main/LICENSE).
