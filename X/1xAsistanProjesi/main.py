import speech_recognition as sr
import pyttsx3
import ollama
import json
import os
import datetime
import time
import sys
import requests
import random
import subprocess

from commands_help import get_commands_help_text
from config import SYSTEM_TOOLS, CUSTOM_PROGRAMS, MUSIC_FOLDER

config = {
    "MASTER_NAME": "Kubyx",
    "ASSISTANT_NAME": "Mira",
    "WAKE_WORD": "mira",
    "OLLAMA_MODEL": "mistral:latest",
    "ENABLE_SPEECH": False,
    "VOICE_MODULES": True,
    "OLLAMA_SERVER_URL": "http://localhost:11434",
    "CHAT_HISTORY_FILE": "chat_history.json",
    "USER_PROFILE_FILE": "user_profile.json",
    "LLM_TEMPERATURE": 0.7,
    "LLM_TOP_P": 0.9,
    "LLM_MAX_TOKENS": 2048,
    "STT_THRESHOLD": 0.7,
    "TTS_VOICE_ID": None,
    "TTS_RATE": 180,
    "TTS_VOLUME": 1.0
}

def check_ollama_server():
    try:
        response = requests.get(f"{config['OLLAMA_SERVER_URL']}/api/tags", timeout=5)
        response.raise_for_status()
        models = [model['name'] for model in response.json()['models']]
        if config['OLLAMA_MODEL'] not in models:
            print(f"Uyarı: Ayarlanan model '{config['OLLAMA_MODEL']}' sunucuda bulunamadı.")
            return False
        return True
    except Exception as e:
        print(f"Ollama sunucusu kontrol edilirken bir hata oluştu: {e}")
        return False

def ollama_ask_llm(prompt, chat_history):
    if not check_ollama_server():
        return "Üzgünüm, şu anda benimle konuşamıyorum. Ollama sunucusunda bir sorun var gibi görünüyor."
    messages = [{"role": "user", "content": prompt}]
    for chat_item in chat_history:
        messages.append({"role": chat_item["role"], "content": chat_item["content"]})
    try:
        response = ollama.chat(
            model=config["OLLAMA_MODEL"],
            messages=messages,
            options={
                "temperature": config["LLM_TEMPERATURE"],
                "top_p": config["LLM_TOP_P"],
                "num_predict": config["LLM_MAX_TOKENS"]
            }
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Ollama hatası: {e}")
        return "Üzgünüm, bir sorun oluştu ve yanıt veremiyorum."

def speak(text):
    if not config["ENABLE_SPEECH"] or not config["VOICE_MODULES"]:
        print(f"[SES KAPALI] Asistan: {text}")
        return
    print(f"Asistan: {text}")
    engine = pyttsx3.init()
    if config["TTS_VOICE_ID"]:
        voices = engine.getProperty('voices')
        for voice in voices:
            if config["TTS_VOICE_ID"].lower() in voice.name.lower() or \
               config["TTS_VOICE_ID"].lower() in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
    engine.setProperty('rate', config["TTS_RATE"])
    engine.setProperty('volume', config["TTS_VOLUME"])
    engine.say(text)
    engine.runAndWait()

chat_history = []
user_profile = {}

def load_data():
    global chat_history, user_profile
    try:
        if os.path.exists(config["CHAT_HISTORY_FILE"]):
            with open(config["CHAT_HISTORY_FILE"], 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
        else:
            chat_history = []
        if os.path.exists(config["USER_PROFILE_FILE"]):
            with open(config["USER_PROFILE_FILE"], 'r', encoding='utf-8') as f:
                user_profile = json.load(f)
        else:
            user_profile = {"name": config["MASTER_NAME"], "last_seen": str(datetime.datetime.now())}
    except Exception as e:
        print(f"Veriler yüklenirken hata oluştu: {e}")
        chat_history = []
        user_profile = {"name": config["MASTER_NAME"], "last_seen": str(datetime.datetime.now())}

def save_data():
    try:
        with open(config["CHAT_HISTORY_FILE"], 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=4)
        with open(config["USER_PROFILE_FILE"], 'w', encoding='utf-8') as f:
            json.dump(user_profile, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Veriler kaydedilirken hata oluştu: {e}")

def list_programs():
    lines = []
    lines.append("Açılabilir Varsayılan Sistem Programları:")
    for key in SYSTEM_TOOLS:
        lines.append(f"- {key.title()}")
    lines.append("\nKendi Programların:")
    for key in CUSTOM_PROGRAMS:
        lines.append(f"- {key.title()}")
    return "\n".join(lines)

def open_program_by_name(name):
    name = name.lower().strip()
    # Önce özel programlarda ara
    for prog, path in CUSTOM_PROGRAMS.items():
        if prog in name or name in prog:
            try:
                os.startfile(path)
                return f"{prog.title()} açılıyor."
            except Exception as e:
                return f"{prog.title()} açılamadı: {e}"
    # Sonra sistem araçlarında ara
    for tool, cmd in SYSTEM_TOOLS.items():
        if tool in name or name in tool:
            try:
                subprocess.Popen(cmd)
                return f"{tool.title()} açılıyor."
            except Exception as e:
                return f"{tool.title()} açılamadı: {e}"
    return f"Üzgünüm, '{name}' adlı bir program bulamadım."

def play_random_music():
    # Müzik klasöründeki dosyaları bul
    if not os.path.isdir(MUSIC_FOLDER):
        return "Müzik klasörü bulunamadı veya tanımlı değil."
    music_files = [f for f in os.listdir(MUSIC_FOLDER)
                   if f.lower().endswith(('.mp3', '.wav', '.ogg', '.flac'))]
    if not music_files:
        return "Müzik klasöründe çalınabilir dosya yok."
    chosen = random.choice(music_files)
    file_path = os.path.join(MUSIC_FOLDER, chosen)
    try:
        os.startfile(file_path)
        return f"Müzik çalınıyor: {chosen}"
    except Exception as e:
        return f"Müzik çalınamadı: {e}"

def execute_command(command_text):
    command_text = command_text.lower().strip()
    response = ""

    if "saat kaç" in command_text:
        response = datetime.datetime.now().strftime("%H:%M")
    elif "tarih ne" in command_text or "bugün ayın kaçı" in command_text:
        response = datetime.datetime.now().strftime("%d %B %Y")
    elif "merhaba" in command_text or "selam" in command_text:
        response = f"Merhaba {user_profile.get('name', 'efendim')}, size nasıl yardımcı olabilirim?"
    elif "kendini tanıt" in command_text:
        response = f"Ben {config['ASSISTANT_NAME']}, {user_profile.get('name', 'size')} yardımcı olmak için tasarlanmış bir yapay zeka asistanıyım."
    elif "nasılsın" in command_text:
        response = "Ben bir yapay zekayım, bir hissim yok. Ama sizin iyi olduğunuzu umuyorum."
    elif "teşekkür ederim" in command_text or "sağ ol" in command_text:
        response = "Rica ederim, her zaman hizmetinizdeyim."
    elif "uygulamayı aç" in command_text:
        app_name = command_text.replace("uygulamayı aç", "").strip()
        if not app_name:
            response = "Hangi uygulamayı açmamı istersiniz?"
        else:
            response = open_program_by_name(app_name)
    elif "programları listele" in command_text or "açılabilir programlar" in command_text:
        response = list_programs()
    elif "kapat" in command_text and "uygulamayı" in command_text:
        response = "Üzgünüm, henüz uygulama kapatma yeteneğim yok."
    elif "arama yap" in command_text or "internet'te ara" in command_text:
        query = command_text.replace("arama yap", "").replace("internet'te ara", "").strip()
        if query:
            import webbrowser
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
            response = f"{query} için internette arama yapılıyor."
        else:
            response = "Ne aramamı istersiniz?"
    elif "youtube aç" in command_text:
        import webbrowser
        webbrowser.open("http://youtube.com")
        response = "YouTube açılıyor."
    elif "müzik çal" in command_text:
        response = play_random_music()
    elif "bilgisayarı kapat" in command_text or "bilgisayarı yeniden başlat" in command_text:
        response = "Bu komutlar için iznim yok ve sistem güvenliği nedeniyle doğrudan bu işlemleri yapmam önerilmez."
    elif "yardım" in command_text:
        response = get_commands_help_text()
    elif "dur" in command_text or "kapat kendini" in command_text or "çıkış" in command_text:
        response = "Görüşmek üzere, kendinize iyi bakın!"
        speak(response)
        save_data()
        sys.exit()
    else:
        response = ollama_ask_llm(command_text, chat_history)
    return response

if __name__ == "__main__":
    load_data()
    print("Asistan başlatıldı. Yardım almak için 'yardım' veya 'programları listele' yazabilirsin.")

    while True:
        try:
            user_input = input("Komutunuzu girin: ").strip()
            if not user_input:
                continue
            print(f"Gelen komut: {user_input}")
            reply = execute_command(user_input)
            if reply:
                chat_history.append({"role": "user", "content": user_input})
                chat_history.append({"role": "assistant", "content": reply})
                print(f"Asistan: {reply}")
                speak(reply)
            save_data()
        except KeyboardInterrupt:
            print("\nKapatılıyor...")
            speak("Kapatılıyor.")
            save_data()
            break
        except Exception as e:
            print(f"Hata: {e}")
            speak("Bir hata oluştu.")
