import subprocess
import sys

def service_action(params):
    islem = params.get("islem")
    servis = params.get("servis")
    if not islem or not servis:
        return "Hatalı parametre: islem ve servis belirtilmeli."
    try:
        if sys.platform.startswith("win"):
            if islem == "başlat":
                subprocess.check_call(["sc", "start", servis])
                return f"{servis} servisi başlatıldı."
            elif islem == "durdur":
                subprocess.check_call(["sc", "stop", servis])
                return f"{servis} servisi durduruldu."
            elif islem == "durum":
                output = subprocess.check_output(["sc", "query", servis], text=True)
                return f"{servis} servisi durumu:\n{output}"
            else:
                return "Bilinmeyen servis işlemi."
        else:
            if islem == "başlat":
                subprocess.check_call(["systemctl", "start", servis])
                return f"{servis} servisi başlatıldı."
            elif islem == "durdur":
                subprocess.check_call(["systemctl", "stop", servis])
                return f"{servis} servisi durduruldu."
            elif islem == "durum":
                output = subprocess.check_output(["systemctl", "status", servis], text=True)
                return f"{servis} servisi durumu:\n{output}"
            else:
                return "Bilinmeyen servis işlemi."
    except Exception as e:
        return f"Servis işlem hatası: {e}"
