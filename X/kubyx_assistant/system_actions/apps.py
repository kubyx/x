import subprocess
import os
import sys

def open_app(params):
    uygulama = params.get("uygulama")
    if not uygulama:
        return "Hatalı parametre: uygulama adı belirtilmeli."
    try:
        if sys.platform.startswith("win"):
            os.startfile(uygulama)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", uygulama])
        else:
            subprocess.Popen([uygulama])
        return f"{uygulama} uygulaması başlatıldı."
    except Exception as e:
        return f"Uygulama başlatma hatası: {e}"
