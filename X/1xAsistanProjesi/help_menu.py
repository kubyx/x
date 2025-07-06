import json
import os

def print_help_menu(json_path="commands.json"):
    # Dosyanın varlığını kontrol et
    if not os.path.exists(json_path):
        print(f"'{json_path}' bulunamadı!")
        return

    # JSON'u oku
    with open(json_path, "r", encoding="utf-8") as f:
        komutlar = json.load(f)

    print("\n" + "#"*45)
    print("#         1xAsistanProjesi Yardım         #")
    print("#" * 45 + "\n")

    for kategori, komut_listesi in komutlar.items():
        print(f"{kategori.upper()}:")
        for item in komut_listesi:
            print(f"  - {item['komut']}: {item['aciklama']}")
        print()  # kategori arası boşluk

if __name__ == "__main__":
    print_help_menu()
