COMMANDS = [
    {"komut": "saat kaç", "açıklama": "Şu anki saati söyler."},
    {"komut": "tarih ne / bugün ayın kaçı", "açıklama": "Bugünün tarihini söyler."},
    {"komut": "merhaba / selam", "açıklama": "Kullanıcıyı selamlar."},
    {"komut": "kendini tanıt", "açıklama": "Asistan kendini tanıtır."},
    {"komut": "nasılsın", "açıklama": "Asistanın durumu hakkında esprili cevap verir."},
    {"komut": "teşekkür ederim / sağ ol", "açıklama": "Teşekkürleri kabul eder."},
    {"komut": "yardım", "açıklama": "Tüm kullanılabilir komutları ve açıklamalarını gösterir."},
    {"komut": "dur / kapat kendini / çıkış", "açıklama": "Programı kapatır."},
    {"komut": "uygulamayı aç [uygulama adı]", "açıklama": "Belirtilen uygulamayı açar (ör: notepad, chrome veya kendi özel listen)."},
    {"komut": "programları listele / açılabilir programlar", "açıklama": "Açabileceği tüm programları listeler."},
    {"komut": "çalıştır [komut]", "açıklama": "Gelişmiş komutları LLM'e iletir."},
    {"komut": "arama yap [konu] / internet'te ara [konu]", "açıklama": "Google'da arama yapar."},
    {"komut": "youtube aç", "açıklama": "YouTube'u açar."},
    {"komut": "müzik çal", "açıklama": "Bilgisayarındaki müzik klasöründen rastgele müzik çalar."},
    {"komut": "kayıt defteri / hizmetler / görev yöneticisi ...", "açıklama": "Windows sistem araçlarını açar (config.py'de detaylar)."},
    {"komut": "calc / notepad / paint", "açıklama": "Hesap makinesi, not defteri, paint gibi uygulamaları açar."},
]

def print_commands_help():
    print("Kullanılabilir Komutlar:\n")
    for item in COMMANDS:
        print(f"- {item['komut']}: {item['açıklama']}")

def get_commands_help_text():
    return "\n".join([f"- {item['komut']}: {item['açıklama']}" for item in COMMANDS])
