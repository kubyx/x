import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ollama'nın varsayılan endpoint'i
MODEL = "turkish-llm"  # Kendi sistemindeki model ismini buraya yaz (ör: openhermes, mistral, orca, mixtral, phi3, vs.)

# Prompt şablonu: Komutu analiz edip, hangi sistem_actions modülünü ve parametreleri kullanacağını döndür
SYSTEM_PROMPT = """
Sen bir Python asistanısın. Kullanıcıdan gelen Türkçe doğal dil komutunu analiz et ve aşağıdaki formata uygun şekilde, hangi system_actions modülünü ve hangi parametrelerle çağıracağını JSON olarak döndür.

MODÜLLER ve ÖRNEK PARAMETRELER:
- files: copy_file({ "kaynak": "C:/A.txt", "hedef": "C:/B.txt" })
- apps: open_app({ "uygulama": "notepad.exe" })
- services: service_action({ "islem": "başlat", "servis": "wuauserv" })
- registry: registry_action({ "islem": "oku", "anahtar": "ANAHTAR_YOLU", "deger_adi": "DEĞER" })
- media: media_action({ "islem": "oynat", "dosya": "C:/Muzik/ornek.mp3" })
- menu: menu_action({ "islem": "göster", "menu": ["Dosya", "Ayarlar", "Çıkış"] })

Dönüş formatı: 
{
  "modul": "apps",
  "fonksiyon": "open_app",
  "parametreler": {
      "uygulama": "notepad.exe"
  }
}

Sadece bu formatta ve kod bloğu olmadan döndür!
"""

def llm_parse_command(command):
    payload = {
        "model": MODEL,
        "prompt": f"{SYSTEM_PROMPT}\nKullanıcı komutu: {command}\nYanıt:",
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()['response']
        # Sadece JSON kısmını almak için (bazı modeller başına/sonuna metin ekleyebilir)
        first_brace = result.find('{')
        last_brace = result.rfind('}')
        json_str = result[first_brace:last_brace+1]
        return json.loads(json_str)
    except Exception as e:
        return None
