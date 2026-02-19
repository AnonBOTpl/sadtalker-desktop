# SadTalker Desktop - PowerShell Installer v3
param([string]$InstallerDir = $PSScriptRoot)

$Host.UI.RawUI.WindowTitle = "SadTalker Desktop - Installer"
$InstallerDir = $InstallerDir.Trim('"', "'", '\', '.')
$SAD_DIR = "$InstallerDir\SadTalker"

# ── Helpers ───────────────────────────────────────────────────────────────────
function Header {
    Clear-Host
    Write-Host ""
    Write-Host "  +----------------------------------------------------+" -ForegroundColor Cyan
    Write-Host "  |       SadTalker Desktop  -  Installer  v3          |" -ForegroundColor Cyan
    Write-Host "  |       github.com/OpenTalker/SadTalker               |" -ForegroundColor DarkCyan
    Write-Host "  +----------------------------------------------------+" -ForegroundColor Cyan
    Write-Host ""
}
function OK   ($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function INFO ($msg) { Write-Host "  [..] $msg" -ForegroundColor Cyan }
function WARN ($msg) { Write-Host "  [!]  $msg" -ForegroundColor Yellow }
function ERR  ($msg) { Write-Host "  [X]  $msg" -ForegroundColor Red }
function STEP ($msg) { Write-Host ""; Write-Host "  --- $msg" -ForegroundColor Magenta }

function Pause-Key ($msg = "Press any key to continue...") {
    Write-Host ""; Write-Host "  $msg" -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Show-Bar ($label, $pct) {
    $fill  = "#" * [int]($pct / 5)
    $empty = " " * (20 - [int]($pct / 5))
    Write-Host "`r  [$fill$empty] $pct%  $label        " -NoNewline -ForegroundColor Cyan
}

function Refresh-Path {
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH","User") + ";" +
                "$env:USERPROFILE\.cargo\bin;$env:USERPROFILE\.local\bin"
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 0 - Git
# ══════════════════════════════════════════════════════════════════════════════
function Install-Git {
    STEP "Checking Git..."
    try { & git --version 2>&1 | Out-Null; OK "Git found."; return } catch {}

    INFO "Git not found. Downloading installer..."
    $url = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
    $exe = "$env:TEMP\git-installer.exe"
    try {
        (New-Object System.Net.WebClient).DownloadFile($url, $exe)
        INFO "Installing Git silently..."
        Start-Process -FilePath $exe -ArgumentList "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS" -Wait
        Remove-Item $exe -ErrorAction SilentlyContinue
        Refresh-Path
        OK "Git installed."
    } catch {
        ERR "Failed to install Git: $_"
        ERR "Install manually: https://git-scm.com/download/win"
        exit 1
    }
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 - Clone repo
# ══════════════════════════════════════════════════════════════════════════════
function Clone-Repo {
    STEP "Cloning SadTalker repository..."

    if ([System.IO.File]::Exists("$SAD_DIR\inference.py")) {
        OK "Repository already exists, skipping clone."
    } else {
        INFO "Cloning from GitHub (this may take a while)..."
        cmd /c "git clone https://github.com/OpenTalker/SadTalker.git `"$SAD_DIR`""
        if ($LASTEXITCODE -ne 0) { ERR "git clone failed (code $LASTEXITCODE)"; exit 1 }
        OK "Repository cloned to: $SAD_DIR"
    }

    $appSrc = "$InstallerDir\sadtalker_app.py"
    $appDst = "$SAD_DIR\sadtalker_app.py"
    if ([System.IO.File]::Exists($appSrc)) {
        [System.IO.File]::Copy($appSrc, $appDst, $true)
        OK "sadtalker_app.py copied to repo."
    } else {
        Write-Host ""
        Write-Host "  +----------------------------------------------------+" -ForegroundColor Red
        Write-Host "  |   sadtalker_app.py NOT FOUND next to installer!    |" -ForegroundColor Red
        Write-Host "  |   Copy sadtalker_app.py to:                        |" -ForegroundColor Red
        Write-Host "  |   $SAD_DIR" -ForegroundColor Yellow
        Write-Host "  |   before launching the app.                        |" -ForegroundColor Red
        Write-Host "  +----------------------------------------------------+" -ForegroundColor Red
        Write-Host ""
        Pause-Key "Press any key to continue installation anyway..."
    }
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 - Python 3.9
# ══════════════════════════════════════════════════════════════════════════════
function Install-Python {
    STEP "Checking Python 3.9..."
    foreach ($c in @("python", "python3")) {
        try {
            $ver = & $c --version 2>&1
            if ($ver -match "Python 3\.9") { OK "Python 3.9 found ($c)."; return $c }
        } catch {}
    }
    try {
        $ver = & py -3.9 --version 2>&1
        if ($ver -match "3\.9") { OK "Python 3.9 found (py launcher)."; return "py -3.9" }
    } catch {}

    WARN "Python 3.9 not found. Downloading..."
    $url = "https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"
    $exe = "$env:TEMP\python-3.9.13-amd64.exe"
    (New-Object System.Net.WebClient).DownloadFile($url, $exe)
    Start-Process -FilePath $exe -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0" -Wait
    Remove-Item $exe -ErrorAction SilentlyContinue
    Refresh-Path
    try {
        $ver = & python --version 2>&1
        if ($ver -match "3\.9") { OK "Python 3.9 installed."; return "python" }
    } catch {}
    ERR "Python install failed. Install manually and re-run."; exit 1
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 - uv
# ══════════════════════════════════════════════════════════════════════════════
function Install-UV {
    STEP "Checking uv..."
    try { $ver = & uv --version 2>&1; OK "uv found: $ver"; return } catch {}
    INFO "Installing uv..."
    powershell -NoProfile -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex" 2>&1 | Out-Null
    Refresh-Path
    try { $ver = & uv --version 2>&1; OK "uv installed: $ver" } catch { ERR "uv install failed."; exit 1 }
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 - venv
# ══════════════════════════════════════════════════════════════════════════════
function Create-Venv {
    STEP "Creating virtual environment (.venv)..."
    $venvPy = "$SAD_DIR\.venv\Scripts\python.exe"
    if ([System.IO.File]::Exists($venvPy)) { OK ".venv already exists."; return $venvPy }
    & uv venv "$SAD_DIR\.venv" --python 3.9 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { ERR "Failed to create venv!"; exit 1 }
    OK ".venv created."
    return $venvPy
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5 - PyTorch (always ask user)
# ══════════════════════════════════════════════════════════════════════════════
function Install-PyTorch ($venvPy) {
    STEP "PyTorch / CUDA version selection..."

    # Try to detect CUDA version and show as hint
    $cudaHint = ""
    try {
        $smiOut = cmd /c "nvidia-smi" 2>&1 | Out-String
        if ($smiOut -match "CUDA Version:\s*([\d.]+)") {
            $cudaHint = $Matches[1]
            OK "nvidia-smi detected CUDA Version: $cudaHint"
        }
    } catch {}

    Write-Host ""
    Write-Host "  Select PyTorch version to install:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1]  CUDA 12.1  - GTX 10xx/16xx/20xx/30xx/40xx (driver 525+)" -ForegroundColor White
    Write-Host "  [2]  CUDA 11.8  - RTX 20xx/30xx (driver 450-524)" -ForegroundColor White
    Write-Host "  [3]  CUDA 11.3  - GTX 9xx/10xx  (driver 418-449)" -ForegroundColor White
    Write-Host "  [4]  CPU only   - no NVIDIA GPU" -ForegroundColor DarkGray
    Write-Host ""
    if ($cudaHint) {
        Write-Host "  >>> Auto-detected CUDA $cudaHint - pick the matching option above <<<" -ForegroundColor Green
    } else {
        Write-Host "  >>> Run 'nvidia-smi' in CMD to check your CUDA version <<<" -ForegroundColor Yellow
    }
    Write-Host ""

    $pkg = $null
    do {
        $choice = Read-Host "  Your choice (1/2/3/4)"
        switch ($choice.Trim()) {
            "1" {
                INFO "CUDA 12.1 -> PyTorch cu121"
                & uv pip install --python "$venvPy" "torch==2.1.0+cu121" "torchvision==0.16.0+cu121" "torchaudio==2.1.0" --extra-index-url "https://download.pytorch.org/whl/cu121"
                $pkg = "done"
            }
            "2" {
                INFO "CUDA 11.8 -> PyTorch cu118"
                & uv pip install --python "$venvPy" "torch==2.0.1+cu118" "torchvision==0.15.2+cu118" "torchaudio==2.0.2" --extra-index-url "https://download.pytorch.org/whl/cu118"
                $pkg = "done"
            }
            "3" {
                INFO "CUDA 11.3 -> PyTorch cu113"
                & uv pip install --python "$venvPy" "torch==1.12.1+cu113" "torchvision==0.13.1+cu113" "torchaudio==0.12.1" --extra-index-url "https://download.pytorch.org/whl/cu113"
                $pkg = "done"
            }
            "4" {
                INFO "CPU only"
                & uv pip install --python "$venvPy" torch torchvision torchaudio
                $pkg = "done"
            }
            default { WARN "Please enter 1, 2, 3 or 4." }
        }
    } while (-not $pkg)

    if ($LASTEXITCODE -eq 0) { OK "PyTorch installed." }
    else { ERR "PyTorch installation failed!"; exit 1 }
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 6 - pip packages
# ══════════════════════════════════════════════════════════════════════════════
function Install-Packages ($venvPy) {
    STEP "Installing Python dependencies..."

    $packages = @(
        @{ pkg = "setuptools<70";  label = "setuptools (pkg_resources fix)" },
        @{ pkg = "cmake";          label = "cmake (required by dlib)" },
        @{ pkg = "dlib";           label = "dlib (face detection)" },
        @{ pkg = "librosa==0.9.2"; label = "librosa 0.9.2 (audio)" },
        @{ pkg = "gfpgan";         label = "gfpgan (face enhancer)" },
        @{ pkg = "basicsr";        label = "basicsr" },
        @{ pkg = "facexlib";       label = "facexlib" },
        @{ pkg = "gradio==3.41.2"; label = "gradio 3.41.2" },
        @{ pkg = "customtkinter";  label = "customtkinter (GUI)" },
        @{ pkg = "pillow";         label = "pillow (images)" },
        @{ pkg = "ffmpeg-python";  label = "ffmpeg-python" }
    )

    $i = 0
    foreach ($item in $packages) {
        $i++
        $pct = [int]($i / $packages.Count * 100)
        Show-Bar $item.label $pct
        & uv pip install --python "$venvPy" $item.pkg 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            WARN "Problem with $($item.pkg) - retrying with --no-deps..."
            & uv pip install --python "$venvPy" $item.pkg --no-deps 2>&1 | Out-Null
        }
    }
    Write-Host ""
    OK "All packages installed."

    if ([System.IO.File]::Exists("$SAD_DIR\requirements.txt")) {
        INFO "Installing requirements.txt..."
        & uv pip install --python "$venvPy" -r "$SAD_DIR\requirements.txt" 2>&1 | Out-Null
        OK "requirements.txt done."
    }
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 7 - Icon
# ══════════════════════════════════════════════════════════════════════════════
function Create-Icon ($venvPy) {
    STEP "Creating app icon..."
    $icoPath = "$SAD_DIR\sadtalker.ico"
    if ([System.IO.File]::Exists($icoPath)) { OK "Icon already exists."; return $icoPath }

    $pyScript = @'
from PIL import Image, ImageDraw
import sys

def make_ico(path):
    sizes = [16, 32, 48, 64, 128, 256]
    imgs = []
    for sz in sizes:
        img  = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for r in range(sz // 2, 0, -1):
            c = int(40 + 180 * r / (sz // 2))
            a = int(255 * r / (sz // 2))
            draw.ellipse([sz//2-r, sz//2-r, sz//2+r, sz//2+r], fill=(c//4, c//5, c, a))
        m = sz // 2
        fr = int(sz * 0.28)
        draw.ellipse([m-fr, m-fr, m+fr, m+fr], fill=(230, 230, 255, 220))
        ey = m - int(fr * 0.2)
        er = max(1, int(fr * 0.15))
        draw.ellipse([m-int(fr*0.4)-er, ey-er, m-int(fr*0.4)+er, ey+er], fill=(40,40,80,255))
        draw.ellipse([m+int(fr*0.4)-er, ey-er, m+int(fr*0.4)+er, ey+er], fill=(40,40,80,255))
        my = m + int(fr * 0.3)
        mw = int(fr * 0.5)
        mh = int(fr * 0.2)
        draw.arc([m-mw, my-mh, m+mw, my+mh], start=0, end=180, fill=(40,40,80,255), width=max(1,sz//32))
        imgs.append(img)
    imgs[0].save(path, format="ICO", sizes=[(s,s) for s in sizes], append_images=imgs[1:])
    print("Icon saved: " + path)

make_ico(sys.argv[1])
'@

    $tmpPy = "$env:TEMP\make_ico.py"
    [System.IO.File]::WriteAllText($tmpPy, $pyScript, [System.Text.UTF8Encoding]::new($false))
    & $venvPy $tmpPy $icoPath 2>&1 | Out-Null
    Remove-Item $tmpPy -ErrorAction SilentlyContinue

    if ([System.IO.File]::Exists($icoPath)) { OK "Icon created." }
    else { WARN "Could not create icon - will use default." }
    return $icoPath
}

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 8 - Desktop shortcut
# ══════════════════════════════════════════════════════════════════════════════
function Create-Shortcut ($icoPath) {
    STEP "Creating desktop shortcut..."
    $desktop   = [Environment]::GetFolderPath("Desktop")
    $lnkPath   = "$desktop\SadTalker Desktop.lnk"
    $batLaunch = "$SAD_DIR\launch.bat"

    $launchContent = "@echo off`r`ncd /d `"%~dp0`"`r`ncall .venv\Scripts\activate`r`npython sadtalker_app.py`r`n"
    [System.IO.File]::WriteAllText($batLaunch, $launchContent, [System.Text.ASCIIEncoding]::new())

    $wsh = New-Object -ComObject WScript.Shell
    $lnk = $wsh.CreateShortcut($lnkPath)
    $lnk.TargetPath       = $batLaunch
    $lnk.WorkingDirectory = $SAD_DIR
    $lnk.WindowStyle      = 1
    $lnk.Description      = "SadTalker Desktop - talking head generator"
    if ($icoPath -and [System.IO.File]::Exists($icoPath)) { $lnk.IconLocation = "$icoPath,0" }
    $lnk.Save()
    OK "Shortcut created: $lnkPath"
}

# ══════════════════════════════════════════════════════════════════════════════
#  FINISH MENU
# ══════════════════════════════════════════════════════════════════════════════
function Show-FinishMenu {
    Write-Host ""
    Write-Host "  +----------------------------------------------------+" -ForegroundColor Green
    Write-Host "  |   Installation complete!                            |" -ForegroundColor Green
    Write-Host "  +----------------------------------------------------+" -ForegroundColor Green
    Write-Host ""
    Write-Host "  +----------------------------------------------------+" -ForegroundColor Yellow
    Write-Host "  |   BEFORE FIRST USE - required steps:               |" -ForegroundColor Yellow
    Write-Host "  |                                                     |" -ForegroundColor Yellow
    Write-Host "  |   1. Launch the app                                 |" -ForegroundColor Yellow
    Write-Host "  |   2. Go to the [Setup] tab                         |" -ForegroundColor Yellow
    Write-Host "  |   3. Click 'Download models' (~2 GB)               |" -ForegroundColor Yellow
    Write-Host "  |      Without models the app cannot generate video. |" -ForegroundColor Yellow
    Write-Host "  +----------------------------------------------------+" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1]  Launch SadTalker Desktop now" -ForegroundColor Cyan
    Write-Host "  [2]  Open app folder in Explorer" -ForegroundColor Cyan
    Write-Host "  [3]  Exit installer" -ForegroundColor DarkGray
    Write-Host ""

    do {
        $choice = Read-Host "  Your choice (1/2/3)"
        switch ($choice.Trim()) {
            "1" { OK "Starting..."; Start-Process -FilePath "$SAD_DIR\launch.bat" -WorkingDirectory $SAD_DIR; exit 0 }
            "2" { explorer.exe $SAD_DIR; Show-FinishMenu; return }
            "3" { Write-Host ""; Write-Host "  Goodbye! Use the desktop shortcut to launch." -ForegroundColor DarkGray; Start-Sleep 1; exit 0 }
            default { WARN "Enter 1, 2 or 3." }
        }
    } while ($true)
}

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
Header
Write-Host "  Install dir: $SAD_DIR" -ForegroundColor DarkGray
Write-Host ""

Install-Git
Clone-Repo
$pyCmd  = Install-Python
Install-UV
$venvPy = Create-Venv
Install-PyTorch $venvPy
Install-Packages $venvPy
$icoPath = Create-Icon $venvPy
Create-Shortcut $icoPath

Show-FinishMenu