import os

# === LLM Ayarları ve Sistem Araçları ===
DEFAULT_LLM_API = "http://localhost:11434/api/generate"
LLM_MODELS = ["llama3", "mistral", "phi3", "tinyllama"]
DEFAULT_LLM_MODEL = "mistral"
ENABLE_SPEECH = False
MAX_HISTORY = 40
PLUGIN_FOLDER = "plugins"

SYSTEM_TOOLS = {
    "kayıt defteri": "regedit",
    "hizmetler": "services.msc",
    "görev yöneticisi": "taskmgr",
    "grup ilkesi": "gpedit.msc",
    "olay görüntüleyici": "eventvwr.msc",
    "bilgisayar yönetimi": "compmgmt.msc",
    "disk yönetimi": "diskmgmt.msc",
    "aygıt yöneticisi": "devmgmt.msc",
    "sistem yapılandırması": "msconfig",
    "güvenlik duvarı": "wf.msc",
    "ağ bağlantıları": "ncpa.cpl",
    "sistem bilgisi aracı": "msinfo32",
    "program ekle kaldır": "appwiz.cpl",
    "denetim masası": "control",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "calc": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
}

# Kendi bilgisayarındaki özel programlar (KISALTMALAR ve YOL)
CUSTOM_PROGRAMS = {
    "acronis": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Acronis True Image.lnk",
    "ashampoo driver updater": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Ashampoo Driver Updater.lnk",
    "jarvis": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\J.A.V.I.S\Jarvis.lnk",
    "media player classic": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\K-Lite Codec Pack\Media Player Classic.lnk",
    "excel": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Microsoft Office Excel 2007.lnk",
    "word": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office\Microsoft Office Word 2007.lnk",
    "opera": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Opera Browser.lnk",
    "poweriso": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerISO\PowerISO.lnk",
    "powershell 7": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerShell\PowerShell 7 (x64).lnk",
    "pycharm": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\JetBrains\PyCharm 2025.1.1.1.lnk",
    "idle": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Python 3.9\IDLE (Python 3.9 64-bit).lnk",
    "rainmeter": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Rainmeter.lnk",
    "age2hd": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\by.xatab\Run Age2HD.lnk",
    "srs9": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\SRS9\Subliminal Recording System 9.0.lnk",
    "visual studio 2022": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Visual Studio 2022.lnk",
    "vmware": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\VMware\VMware Workstation Pro.lnk",
    "admin tools": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Administrative Tools.lnk",
    "winrar": r"C:\Users\Master\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\WinRAR\WinRAR.lnk",
}

# Müzik klasörü yolu (BURAYI KENDİNE GÖRE DEĞİŞTİREBİLİRSİN)
MUSIC_FOLDER = r"D:\Muzik"
