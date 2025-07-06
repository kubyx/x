# Sesli Komut Asistanı

Türkçe doğal dil ile sistem üzerinde dosya, uygulama, servis, medya ve daha fazlasını sesli komutlarla yönetebileceğiniz modüler asistan projesi.

## Özellikler

- **Otomatik sesli tanıma ve yanıt**
- **Dosya işlemleri**: Kopyala, sil, taşı
- **Uygulama başlatma**
- **Sistem servislerini kontrol etme**
- **Medya dosyalarını oynatma/durdurma**
- **Windows Registry yönetimi**
- **Menü gösterimi ve yönetimi**
- **Ollama Türkçe LLM entegrasyonu**
- **Kolay yapılandırma ve genişletilebilir modül sistemi**

## Kurulum

1. Gerekli paketleri yükleyin:
    ```sh
    pip install -r requirements.txt
    ```

2. `config.py` dosyasını isteğinize göre düzenleyin.

## Kullanım

Terminalden çalıştırmak için:
```sh
python main.py
```

Uygulama, sesli komutunuzu bekler ve uygun sistemi eylemini gerçekleştirir.

## Dosya Yapısı

- `main.py` : Başlatıcı ve ana döngü
- `dialogue_manager.py` : Diyalog yönetimi
- `llm_interface.py` : Dil modeli ile etkileşim
- `voice_interface.py` : Sesli giriş/çıkış
- `system_actions/` : Sistem işlemleri modülleri
- `config.py` : Ayarlar

## Katkı

Katkıda bulunmak için PR gönderebilir veya issue açabilirsiniz.

## Lisans

MIT