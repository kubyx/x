import subprocess
import sys

def media_action(params):
    islem = params.get("islem")
    dosya = params.get("dosya")
    if not islem or not dosya:
        return "Hatalı parametre: islem ve dosya belirtilmeli."
    try:
        if islem == "oynat":
            if sys.platform.startswith("win"):
                os.startfile(dosya)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", dosya])
            else:
                subprocess.Popen(["xdg-open", dosya])
            return f"{dosya} medya dosyası oynatılıyor."
        elif islem == "durdur":
            # Basit örnek: medya oynatmayı durdurmak için tüm medya oynatıcılarını sonlandır
            if sys.platform.startswith("win"):
                subprocess.call(["taskkill", "/IM", "wmplayer.exe", "/F"])
            else:
                subprocess.call(["pkill", "vlc"])
            return "Medya oynatıcı durduruldu."
        else:
            return "Bilinmeyen medya işlemi."
    except Exception as e:
        return f"Medya işlem hatası: {e}"
