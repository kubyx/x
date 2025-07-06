from voice_interface import recognize_speech, speak_text
from llm_interface import llm_parse_command
from help_utils import list_commands
import system_actions.files as files
import system_actions.apps as apps
import system_actions.services as services
import system_actions.registry as registry
import system_actions.media as media
import system_actions.menu as menu

MODUL_MAP = {
    "files": files,
    "apps": apps,
    "services": services,
    "registry": registry,
    "media": media,
    "menu": menu
}

def run_llm_command(parsed):
    modul = parsed.get("modul")
    fonksiyon = parsed.get("fonksiyon")
    parametreler = parsed.get("parametreler", {})
    modul_modul = MODUL_MAP.get(modul)
    if not modul_modul or not hasattr(modul_modul, fonksiyon):
        return "Bu komut için uygun modül bulunamadı."
    return getattr(modul_modul, fonksiyon)(parametreler)

def get_user_input(method):
    if method == "ses":
        return recognize_speech()
    else:
        return input("Komutunuzu yazın (çıkmak için 'çık' yazın): ")

def main():
    print("Komut giriş türü seçin: [1] Yazı (öntanımlı)  [2] Ses")
    secim = input("Seçiminiz (1/2): ").strip()
    method = "ses" if secim == "2" else "yazı"
    if method == "ses":
        speak_text("Asistan hazır! Sesli komutunuzu söyleyin.")
    else:
        print("Asistan hazır! Komutunuzu yazabilirsiniz.")
    while True:
        komut = get_user_input(method)
        # Yardım komutunu LLM'ye göndermeden önce burada yakala!
        if komut and komut.strip().lower() in ["yardım", "help", "?"]:
            komutlar = list_commands()
            msg = "Desteklenen komutlar ve fonksiyonlar:\n" + "\n".join(f"- {k}" for k in komutlar)
            if method == "ses":
                speak_text(msg)
            else:
                print(msg)
            continue
        if not komut:
            if method == "ses":
                speak_text("Sizi anlayamadım.")
            else:
                print("Komut algılanamadı.")
            continue
        if "çık" in komut.lower() or "kapat" in komut.lower():
            if method == "ses":
                speak_text("Görüşmek üzere!")
            else:
                print("Görüşmek üzere!")
            break
        parsed = llm_parse_command(komut)
        if not parsed:
            if method == "ses":
                speak_text("Komut analiz edilemedi veya LLM'den yanıt alınamadı.")
            else:
                print("Komut analiz edilemedi veya LLM'den yanıt alınamadı.")
            continue
        sonuc = run_llm_command(parsed)
        if method == "ses":
            speak_text(str(sonuc))
        else:
            print(sonuc)

if __name__ == "__main__":
    main()
