import shutil
import os

def copy_file(params):
    kaynak = params.get("kaynak")
    hedef = params.get("hedef")
    if not kaynak or not hedef:
        return "Hatalı parametre: kaynak ve hedef belirtilmeli."
    try:
        shutil.copy(kaynak, hedef)
        return f'{kaynak} dosyası {hedef} konumuna kopyalandı.'
    except Exception as e:
        return f"Dosya kopyalama hatası: {e}"

def delete_file(params):
    dosya = params.get("dosya")
    if not dosya:
        return "Hatalı parametre: dosya belirtilmeli."
    try:
        os.remove(dosya)
        return f'{dosya} dosyası silindi.'
    except Exception as e:
        return f"Dosya silme hatası: {e}"

def move_file(params):
    kaynak = params.get("kaynak")
    hedef = params.get("hedef")
    if not kaynak or not hedef:
        return "Hatalı parametre: kaynak ve hedef belirtilmeli."
    try:
        shutil.move(kaynak, hedef)
        return f'{kaynak} dosyası {hedef} konumuna taşındı.'
    except Exception as e:
        return f"Dosya taşıma hatası: {e}"
