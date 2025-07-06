def menu_action(params):
    islem = params.get("islem")
    menu = params.get("menu")
    if not islem or not menu:
        return "Hatalı parametre: islem ve menu belirtilmeli."
    if islem == "göster":
        # Basit örnek: Menü başlıklarını döndür
        if isinstance(menu, list):
            return "Menü:\n" + "\n".join(menu)
        elif isinstance(menu, str):
            return f"Menü: {menu}"
        else:
            return "Geçersiz menü formatı."
    else:
        return "Bilinmeyen menü işlemi."
