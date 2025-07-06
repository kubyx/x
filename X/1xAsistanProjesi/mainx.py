import sys
from help_menu import print_help_menu

def main():
    print("1xAsistan'a hoş geldiniz! Bir komut girin ('çıkış' ile kapatabilirsiniz):\n")

    while True:
        user_input = input("> ").strip().lower()

        # Çıkış komutları
        if user_input in ["çıkış", "kapat", "dur", "kapat kendini"]:
            print("Görüşmek üzere!")
            break

        # Dinamik yardım menüsü çağrısı
        elif "yardım" in user_input:
            print_help_menu()

        # Selamlama
        elif user_input in ["merhaba", "selam"]:
            print("Merhaba! Size nasıl yardımcı olabilirim?")

        # Asistanı tanıtma
        elif user_input == "kendini tanıt":
            print("Ben 1xAsistan, bilgisayarınızda size yardımcı olmak için tasarlandım!")

        # Saat bilgisi
        elif user_input in ["saat kaç"]:
            from datetime import datetime
            print("Şu an saat:", datetime.now().strftime("%H:%M"))

        # Tarih bilgisi
        elif user_input in ["tarih ne", "bugün ayın kaçı"]:
            from datetime import datetime
            print("Bugünün tarihi:", datetime.now().strftime("%Y-%m-%d"))

        # Teşekkür
        elif user_input in ["teşekkür ederim", "sağ ol"]:
            print("Rica ederim, her zaman buradayım!")

        # Bilinmeyen komut
        else:
            print("Bu komutu anlayamadım. Yardım için 'yardım' yazabilirsiniz.")

if __name__ == "__main__":
    main()

