import requests
import subprocess
import shutil
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_LIST_URL = "http://localhost:11434/api/tags"

def list_ollama_models():
    # Ollama'nın /api/tags endpointi ile yüklü modelleri çekiyoruz
    try:
        response = requests.get(OLLAMA_LIST_URL)
        if response.ok:
            tags = response.json().get("models", [])
            if not tags:
                print("Hiç model bulunamadı. Önce bir model yükleyin (örn: ollama pull llama3).")
                return []
            print("Yüklü Modeller:")
            for idx, tag in enumerate(tags, 1):
                print(f"{idx}. {tag['name']}")
            return [tag['name'] for tag in tags]
        else:
            print("Modeller alınamadı:", response.text)
            return []
    except Exception as e:
        print("Modeller alınırken hata:", e)
        return []

def ollama_chat(prompt, model):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=data)
    if response.ok:
        return response.json()["response"].strip()
    else:
        return f"Hata: {response.text}"

def execute_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except Exception as e:
        return f"Hata: {e}"

def copy_file(src, dst):
    try:
        shutil.copy(src, dst)
        return f"{src} -> {dst} kopyalandı."
    except Exception as e:
        return f"Hata: {e}"

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Hata: {e}"

def write_file(path, content):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"{path} başarıyla yazıldı."
    except Exception as e:
        return f"Hata: {e}"

def select_model():
    models = list_ollama_models()
    if not models:
        raise Exception("Hiç model yok. Lütfen önce bir model yükleyin!")
    while True:
        secim = input("Model numarasını girin veya tam model adını yazın: ").strip()
        if secim.isdigit():
            idx = int(secim) - 1
            if 0 <= idx < len(models):
                return models[idx]
            else:
                print("Geçersiz numara.")
        elif secim in models:
            return secim
        else:
            print("Yanlış seçim, tekrar deneyin.")

def main():
    print("Ollama AI Asistan (tam erişimli, offline)")
    model = select_model()
    print(f"Kullanılacak model: {model}")
    print("Çıkmak için: çıkış / exit")
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ["çıkış", "exit", "quit"]:
            print("Çıkılıyor.")
            break

        if user_input.startswith("komut:"):
            komut = user_input.replace("komut:", "", 1).strip()
            print(execute_command(komut))
        elif user_input.startswith("oku:"):
            dosya = user_input.replace("oku:", "", 1).strip()
            print(read_file(dosya))
        elif user_input.startswith("yaz:"):
            try:
                yol, veri = user_input.replace("yaz:", "", 1).split("::", 1)
                print(write_file(yol.strip(), veri))
            except:
                print("Kullanım: yaz: dosya_yolu::içerik")
        elif user_input.startswith("kopyala:"):
            try:
                src, dst = user_input.replace("kopyala:", "", 1).split("->", 1)
                print(copy_file(src.strip(), dst.strip()))
            except:
                print("Kullanım: kopyala: kaynak_yol -> hedef_yol")
        elif user_input.startswith("model:"):
            # Modeli anlık değiştirmek için
            model = select_model()
            print(f"Model {model} olarak değiştirildi.")
        else:
            yanit = ollama_chat(user_input, model)
            print(yanit)

if __name__ == "__main__":
    main()
