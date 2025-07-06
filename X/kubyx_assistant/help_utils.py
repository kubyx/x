import os
import importlib

def list_commands():
    komutlar = []
    actions_dir = os.path.join(os.path.dirname(__file__), "system_actions")
    for filename in os.listdir(actions_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            modul_adi = filename[:-3]
            modul_path = f"system_actions.{modul_adi}"
            try:
                modul = importlib.import_module(modul_path)
                for fonksiyon_adi in dir(modul):
                    if not fonksiyon_adi.startswith("_"):
                        fonksiyon = getattr(modul, fonksiyon_adi)
                        if callable(fonksiyon):
                            komutlar.append(f"{modul_adi}.{fonksiyon_adi}")
            except Exception as e:
                komutlar.append(f"{modul_adi} (modül hatası: {e})")
    return komutlar
