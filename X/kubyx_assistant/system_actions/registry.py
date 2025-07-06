import winreg

def registry_action(params):
    islem = params.get("islem")
    anahtar = params.get("anahtar")
    deger_adi = params.get("deger_adi")
    deger = params.get("deger")
    anahtar_tipi = params.get("anahtar_tipi", winreg.HKEY_CURRENT_USER)

    if not anahtar or not islem:
        return "Hatalı parametre: anahtar ve işlem belirtilmeli."

    try:
        if islem == "oku":
            with winreg.OpenKey(anahtar_tipi, anahtar, 0, winreg.KEY_READ) as key:
                veri, tip = winreg.QueryValueEx(key, deger_adi)
            return f"{anahtar}\\{deger_adi} = {veri} (tip: {tip})"
        elif islem == "yaz":
            with winreg.OpenKey(anahtar_tipi, anahtar, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, deger_adi, 0, winreg.REG_SZ, deger)
            return f"{anahtar}\\{deger_adi} değeri {deger} olarak yazıldı."
        elif islem == "sil":
            with winreg.OpenKey(anahtar_tipi, anahtar, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, deger_adi)
            return f"{anahtar}\\{deger_adi} anahtarı silindi."
        else:
            return "Bilinmeyen işlem tipi."
    except Exception as e:
        return f"Registry işlem hatası: {e}"
