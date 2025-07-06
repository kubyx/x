# -*- coding: utf-8 -*-
import os
import subprocess
import requests
import sys
import platform
import datetime
import threading
import queue
import json
import getpass
import shutil
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

# Ekstra modüller (isteğe bağlı)
try:
    import psutil
except ImportError:
    psutil = None

try:
    import speech_recognition as sr
    import pyttsx3
    from gtts import gTTS
    import playsound
    VOICE_MODULES = True
except ImportError:
    VOICE_MODULES = False

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import paramiko
except ImportError:
    paramiko = None

# === KULLANICI & SİSTEM AYARLARI ===
DEFAULT_LLM_API = "http://localhost:11434/api/generate"
LLM_MODELS = ["llama3", "mistral", "phi3"] # This will be dynamically updated
DEFAULT_LLM_MODEL = "llama3"
ENABLE_SPEECH = False
MAX_HISTORY = 40
PLUGIN_FOLDER = "plugins"
PROFILE_FILE = "user_profile.json"
ALIASES_FILE = "aliases.json"
MACRO_FILE = "macros.json"
CHAT_HISTORY_FILE = "chat_history.txt"

# === GLOBAL DURUM ===
chat_history = []
user_profile = {}
aliases = {}
macros = {}
system_os = platform.system()
current_llm = DEFAULT_LLM_MODEL

# GUI Bileşenleri
output_text = None
input_entry = None
model_dropdown = None

def save_profile():
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(user_profile, f, indent=2)

def load_profile():
    global user_profile
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            user_profile = json.load(f)
    else:
        user_profile = {
            "name": getpass.getuser(),
            "home": os.path.expanduser("~"),
            "created_at": str(datetime.datetime.now())
        }
        save_profile()

def save_aliases():
    with open(ALIASES_FILE, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2)

def load_aliases():
    global aliases
    if os.path.exists(ALIASES_FILE):
        with open(ALIASES_FILE, "r", encoding="utf-8") as f:
            aliases = json.load(f)
    else:
        aliases = {}

def save_macros():
    with open(MACRO_FILE, "w", encoding="utf-8") as f:
        json.dump(macros, f, indent=2)

def load_macros():
    global macros
    if os.path.exists(MACRO_FILE):
        with open(MACRO_FILE, "r", encoding="utf-8") as f:
            macros = json.load(f)
    else:
        macros = {}

def save_history():
    with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as f:
        for entry in chat_history:
            f.write(f"{entry['role']}:{entry['content']}\n")

def load_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    role, content = parts
                    chat_history.append({"role": role, "content": content})


def update_output(message):
    if output_text:
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, message + "\n")
        output_text.see(tk.END)
        output_text.config(state=tk.DISABLED)

# === SESLİ ÇIKIŞ ===
def speak(text):
    if not ENABLE_SPEECH or not VOICE_MODULES:
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        try:
            tts = gTTS(text=text, lang='tr')
            filename = "temp_voice.mp3"
            tts.save(filename)
            playsound.playsound(filename)
            os.remove(filename)
        except Exception:
            pass

# === SESLİ GİRİŞ ===
def listen():
    if not ENABLE_SPEECH or not VOICE_MODULES:
        return "" # GUI will handle text input directly
    r = sr.Recognizer()
    with sr.Microphone() as source:
        update_output("Dinliyorum...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio, language="tr-TR")
    except Exception:
        update_output("Ses algılanamadı, lütfen tekrar deneyin.")
        return ""

# === LLM API'YE SORU SORMA ===
def ask_llm(prompt, history=None, model=None):
    url = DEFAULT_LLM_API
    model = model or current_llm
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.25}
    }
    if history:
        payload["history"] = history[-MAX_HISTORY:]
    try:
        r = requests.post(url, json=payload, timeout=180)
        r.raise_for_status()
        reply = r.json().get("response", "")
        return reply.strip()
    except Exception as e:
        return f"LLM API HATASI: {e}"

# === GGUF'dan Ollama Model Oluşturma ===
def ollama_create_model_from_gguf(gguf_path, model_name):
    """
    HuggingFace'den indirilen GGUF dosyasını Ollama'ya model olarak ekler.
    """
    if not os.path.exists(gguf_path):
        return f"GGUF dosyası bulunamadı: {gguf_path}"
    if not shutil.which("ollama"):
        return "Ollama yüklü değil veya PATH'de değil!"
    # Modelfile oluştur
    modelfile_content = f'FROM ./{os.path.basename(gguf_path)}\nTEMPLATE "llama"\n'
    modelfile_path = os.path.join(os.path.dirname(gguf_path), "Modelfile")
    try:
        with open(modelfile_path, "w", encoding="utf-8") as f:
            f.write(modelfile_content)
    except Exception as e:
        return f"Modelfile yazılamadı: {e}"
    # Ollama create komutu
    prev_dir = os.getcwd()
    try:
        os.chdir(os.path.dirname(gguf_path))
        result = subprocess.run(
            ["ollama", "create", model_name, "--file", "Modelfile"],
            capture_output=True, text=True, timeout=1200
        )
        os.chdir(prev_dir)
        if result.returncode == 0:
            if model_name not in LLM_MODELS:
                LLM_MODELS.append(model_name)
                update_model_dropdown() # Update GUI dropdown
            return f"Model {model_name} başarıyla eklendi ve Ollama ile kullanılabilir!"
        else:
            return f"Ollama create hatası:\n{result.stderr}"
    except Exception as e:
        return f"Ollama model ekleme hatası: {e}"

def ollama_list_models():
    """
    Ollama'da kayıtlı modelleri listeler ve LLM_MODELS listesini günceller.
    """
    global LLM_MODELS
    if not shutil.which("ollama"):
        return "Ollama yüklü değil veya PATH'de değil!"
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            models_output = result.stdout.strip().split('\n')[1:] # Skip header
            new_models = []
            for line in models_output:
                if line.strip():
                    model_name = line.split()[0]
                    new_models.append(model_name)
            LLM_MODELS = list(sorted(list(set(LLM_MODELS + new_models)))) # Add new models and sort
            return result.stdout
        else:
            return f"Ollama list hatası:\n{result.stderr}"
    except Exception as e:
        return f"Ollama model listesi hatası: {e}"

# === PLUGIN YÜKLEME ===
def load_plugins():
    plugins = {}
    if not os.path.exists(PLUGIN_FOLDER):
        os.makedirs(PLUGIN_FOLDER)
    sys.path.insert(0, PLUGIN_FOLDER)
    for fname in os.listdir(PLUGIN_FOLDER):
        if fname.endswith(".py"):
            modname = fname[:-3]
            try:
                mod = __import__(modname)
                if hasattr(mod, "plugin_entry"):
                    plugins[modname] = mod.plugin_entry
            except Exception as e:
                update_output(f"Eklenti yüklenemedi: {modname} ({e})")
    return plugins

# === DOSYA/PROGRAM/SİSTEM İŞLEMLERİ ===
def run_shell_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=180)
        output = result.stdout.strip()
        error = result.stderr.strip()
        if result.returncode == 0:
            return output if output else "Komut başarıyla çalıştı."
        else:
            return f"Hata oluştu:\n{error}"
    except Exception as e:
        return f"Komut çalıştırma hatası: {e}"

def list_files(path="."):
    try:
        files = os.listdir(path)
        return files
    except Exception as e:
        return [f"Hata: {e}"]

def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Hata: {e}"

def write_file(filepath, content):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return "Dosya başarıyla kaydedildi."
    except Exception as e:
        return f"Hata: {e}"

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        return f"{src} -> {dst} taşındı."
    except Exception as e:
        return f"Hata: {e}"

def delete_file(filepath):
    try:
        os.remove(filepath)
        return f"{filepath} silindi."
    except Exception as e:
        return f"Hata: {e}"

def get_system_info():
    info = {
        "OS": platform.platform(),
        "Python": platform.python_version(),
        "User": os.getenv("USERNAME") or os.getenv("USER"),
        "Datetime": str(datetime.datetime.now()),
        "CPU": platform.processor(),
    }
    if psutil:
        info["RAM"] = f"{psutil.virtual_memory().total // (1024*1024)} MB"
        info["Disk"] = f"{psutil.disk_usage('/').total // (1024*1024*1024)} GB"
        info["Yüklü Proses"] = str(len(psutil.pids()))
    return "\n".join([f"{k}: {v}" for k, v in info.items()])

def list_processes():
    if not psutil:
        return "psutil modülü yok."
    lst = []
    for p in psutil.process_iter(['pid', 'name', 'username']):
        lst.append(f"{p.info['pid']} - {p.info['name']} - {p.info['username']}")
    return "\n".join(lst)

def kill_process(pid):
    if not psutil:
        return "psutil modülü yok."
    try:
        p = psutil.Process(int(pid))
        p.terminate()
        return f"{pid} sonlandırıldı."
    except Exception as e:
        return f"Hata: {e}"

# === SSH KOMUTU ===
def ssh_run_cmd(host, user, password, command):
    if not paramiko:
        return "paramiko modülü yok."
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        err = stderr.read().decode()
        ssh.close()
        return output if output else err
    except Exception as e:
        return f"SSH hatası: {e}"

# === İNTERNET ARAMA (DuckDuckGo) ===
def web_search(query):
    if not BeautifulSoup:
        return "beautifulsoup4 modülü yok."
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for a in soup.find_all("a", {"class": "result__a"}, limit=5):
                results.append(f"{a.text.strip()} - {a['href']}")
            return "\n".join(results) if results else "Sonuç bulunamadı."
        else:
            return "Arama başarısız."
    except Exception as e:
        return f"Web arama hatası: {e}"

# === ALIAS VE MAKRO SİSTEMİ ===
def add_alias(alias, command):
    aliases[alias] = command
    save_aliases()
    return f"Alias '{alias}' kaydedildi."

def run_alias(alias):
    if alias in aliases:
        return run_shell_command(aliases[alias])
    else:
        return "Alias yok."

def delete_alias(alias):
    if alias in aliases:
        del aliases[alias]
        save_aliases()
        return f"Alias '{alias}' silindi."
    else:
        return "Alias yok."

def add_macro(name, commands):
    macros[name] = commands
    save_macros()
    return f"Makro '{name}' kaydedildi."

def run_macro(name):
    if name not in macros:
        return "Makro yok."
    results = []
    for cmd in macros[name]:
        results.append(run_shell_command(cmd))
    return "\n".join(results)

def delete_macro(name):
    if name in macros:
        del macros[name]
        save_macros()
    return f"Makro '{name}' silindi."

# === KOMUTLAR ===
def help_menu():
    menu = (
        "\n--- Komutlar ---\n"
        "ai: <soru>       - Soru/istek için LLM'ye danış\n"
        "dosya oku <yol> - Dosya içeriğini göster\n"
        "dosya yaz <yol> - Dosyaya yaz\n"
        "listele <yol>    - Klasör içeriğini göster\n"
        "çalıştır <komut> - Terminal/komut çalıştırır\n"
        "sistem bilgi    - Sistem bilgisi verir\n"
        "prosesler       - Aktif prosesleri listeler\n"
        "sonlandır <pid> - Proses sonlandır\n"
        "ara <kelime>    - İnternette arama\n"
        "ssh <host> <user> <password> <cmd> - Uzaktan komut çalıştır\n"
        "alias ekle <ad> <komut>\n"
        "alias sil <ad>\n"
        "alias çalıştır <ad>\n"
        "makro ekle <ad>\n"
        "makro sil <ad>\n"
        "makro çalıştır <ad>\n"
        "eklentiler      - Yüklü eklentileri listeler\n"
        "kullan <eklenti> <veri> - Eklenti çalıştır\n"
        "model ekle <gguf_yolu> <model_adı> - GGUF dosyasından Ollama modeli ekle\n"
        "model list      - Ollama'daki modelleri listeler\n"
        "model <ad>      - LLM modelini değiştir\n"
        "profil          - Kullanıcı profili göster\n"
        "ses aç / ses kap - Sesli cevap modunu aç/kapat\n"
        "geçmiş          - Son sohbet geçmişi\n"
        "çıkış           - Programı sonlandırır\n"
        "----------------\n"
    )
    return menu

# --- GUI Fonksiyonları ---
def process_command(user_input):
    global ENABLE_SPEECH
    global current_llm

    if not user_input:
        return

    update_output(f"Siz: {user_input}")
    chat_history.append({"role": "user", "content": user_input})

    if user_input.lower() in ("çıkış", "exit", "quit"):
        update_output("Görüşmek üzere!")
        speak("Görüşmek üzere!")
        save_history()
        root.quit()
    elif user_input.lower() in ("yardım", "help"):
        update_output(help_menu())
    # --- GGUF model ekleme ---
    elif user_input.lower().startswith("model ekle"):
        parts = user_input.split()
        if len(parts) >= 4:
            _, _, gguf_path, model_name = parts[:4]
            update_output(ollama_create_model_from_gguf(gguf_path, model_name))
        else:
            update_output("Kullanım: model ekle <gguf_yolu> <model_adı>")
    elif user_input.lower().startswith("model list"):
        update_output(ollama_list_models())
        update_model_dropdown() # Ensure dropdown is updated after listing
    # --- Var olan model seçme ---
    elif user_input.lower().startswith("model"):
        _, model = user_input.split()
        if model in LLM_MODELS:
            current_llm = model
            update_output(f"LLM modeli {model} olarak ayarlandı.")
        else:
            update_output(f"Desteklenen modeller: {', '.join(LLM_MODELS)}")
    elif user_input.lower().startswith("ai:"):
        prompt = user_input[3:].strip()
        reply = ask_llm(prompt, chat_history, current_llm)
        update_output(f"AI: {reply}")
        speak(reply)
        chat_history.append({"role": "assistant", "content": reply})
    elif user_input.lower().startswith("dosya oku"):
        path = user_input[9:].strip()
        update_output(read_file(path))
    elif user_input.lower().startswith("dosya yaz"):
        path = user_input[9:].strip()
        # For GUI, we'll need a separate input for content
        # For simplicity, let's just make it a single-line input for now or open a new window
        # A better implementation would involve a text area for multi-line input
        # For now, let's prompt the user in a message box for the content
        content = messagebox.askstring("Dosyaya Yaz", f"'{path}' dosyasına yazmak istediğiniz içeriği girin:")
        if content is not None:
            update_output(write_file(path, content))
        else:
            update_output("Dosya yazma işlemi iptal edildi.")
    elif user_input.lower().startswith("listele"):
        path = user_input[7:].strip() or "."
        files = list_files(path)
        update_output("\n".join(files))
    elif user_input.lower().startswith("çalıştır"):
        cmd = user_input[9:].strip()
        update_output(run_shell_command(cmd))
    elif user_input.lower().startswith("ara"):
        q = user_input[3:].strip()
        update_output(web_search(q))
    elif user_input.lower() == "sistem bilgi":
        update_output(get_system_info())
    elif user_input.lower() == "prosesler":
        update_output(list_processes())
    elif user_input.lower().startswith("sonlandır"):
        pid = user_input[10:].strip()
        update_output(kill_process(pid))
    elif user_input.lower().startswith("ssh"):
        parts = user_input.split()
        if len(parts) >= 5:
            host, user, password, cmd = parts[1], parts[2], parts[3], " ".join(parts[4:])
            update_output(ssh_run_cmd(host, user, password, cmd))
        else:
            update_output("Kullanım: ssh <host> <user> <password> <cmd>")
    elif user_input.lower().startswith("alias ekle"):
        parts = user_input.split(maxsplit=3)
        if len(parts) >= 4:
            _, _, alias, command = parts[0], parts[1], parts[2], parts[3]
            update_output(add_alias(alias, command))
        else:
            update_output("Kullanım: alias ekle <ad> <komut>")
    elif user_input.lower().startswith("alias sil"):
        parts = user_input.split()
        if len(parts) >= 3:
            _, _, alias = parts[0], parts[1], parts[2]
            update_output(delete_alias(alias))
        else:
            update_output("Kullanım: alias sil <ad>")
    elif user_input.lower().startswith("alias çalıştır"):
        parts = user_input.split()
        if len(parts) >= 3:
            _, _, alias = parts[0], parts[1], parts[2]
            update_output(run_alias(alias))
        else:
            update_output("Kullanım: alias çalıştır <ad>")
    elif user_input.lower().startswith("makro ekle"):
        _, _, name = user_input.split()
        # For macros, we'll need a multi-line input.
        # This is a simplification; a dedicated dialog would be better.
        commands_str = messagebox.askstring("Makro Ekle", f"'{name}' makrosuna eklenecek komutları girin (her komutu yeni satıra yazın):")
        if commands_str is not None:
            commands = [cmd.strip() for cmd in commands_str.split('\n') if cmd.strip()]
            update_output(add_macro(name, commands))
        else:
            update_output("Makro ekleme işlemi iptal edildi.")
    elif user_input.lower().startswith("makro sil"):
        _, _, name = user_input.split()
        update_output(delete_macro(name))
    elif user_input.lower().startswith("makro çalıştır"):
        _, _, name = user_input.split()
        update_output(run_macro(name))
    elif user_input.lower() == "eklentiler":
        if plugins:
            update_output("Yüklü eklentiler: " + ", ".join(plugins.keys()))
        else:
            update_output("Hiç eklenti yüklenmedi.")
    elif user_input.lower().startswith("kullan"):
        parts = user_input.split(maxsplit=2)
        if len(parts) >= 3:
            plugin, data = parts[1], parts[2]
            if plugin in plugins:
                try:
                    result = plugins[plugin](data)
                    update_output(result)
                except Exception as e:
                    update_output(f"Eklenti hatası: {e}")
            else:
                update_output("Eklenti bulunamadı.")
        else:
            update_output("Kullanım: kullan <eklenti> <veri>")
    elif user_input.lower() == "profil":
        update_output(json.dumps(user_profile, indent=2, ensure_ascii=False))
    elif user_input.lower() == "ses aç":
        if VOICE_MODULES:
            ENABLE_SPEECH = True
            update_output("Sesli yanıt modu açıldı.")
        else:
            update_output("Sesli mod için gerekli modüller eksik.")
    elif user_input.lower() == "ses kap":
        ENABLE_SPEECH = False
        update_output("Sesli yanıt modu kapatıldı.")
    elif user_input.lower() == "geçmiş":
        for x in chat_history[-MAX_HISTORY:]:
            update_output(f"{x['role']}: {x['content']}")
    else:
        # AI'dan öneri al: komutun ne olduğunu anlamazsa
        prompt = f"Kullanıcı şu isteği verdi: '{user_input}'. Ne yapmak istediğini analiz et, öneri ve komut ver."
        reply = ask_llm(prompt, chat_history, current_llm)
        update_output(f"AI önerisi: {reply}")
        speak(reply)
        chat_history.append({"role": "assistant", "content": reply})

def send_command():
    user_input = input_entry.get()
    input_entry.delete(0, tk.END) # Clear the input field
    # Run command in a separate thread to prevent GUI from freezing
    threading.Thread(target=process_command, args=(user_input,)).start()

def select_gguf_file():
    file_path = filedialog.askopenfilename(
        title="GGUF Dosyası Seçin",
        filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")]
    )
    if file_path:
        model_name = messagebox.askstring("Model Adı", "Bu model için bir isim girin:")
        if model_name:
            update_output(f"Model ekleniyor: {model_name} from {file_path}")
            threading.Thread(target=lambda: update_output(ollama_create_model_from_gguf(file_path, model_name))).start()
        else:
            update_output("Model adı girilmedi.")
    else:
        update_output("GGUF dosyası seçilmedi.")

def update_model_dropdown():
    global model_dropdown
    # Clear existing options
    model_dropdown['menu'].delete(0, 'end')
    # Add new options
    for model in LLM_MODELS:
        model_dropdown['menu'].add_command(label=model, command=tk._setit(model_var, model))
    model_var.set(current_llm) # Set current model

def set_llm_model(*args):
    global current_llm
    current_llm = model_var.get()
    update_output(f"LLM modeli {current_llm} olarak değiştirildi.")


# === ANA GUI DÖNGÜSÜ ===
def setup_gui():
    global output_text, input_entry, root, model_dropdown, model_var

    root = tk.Tk()
    root.title(f"{user_profile['name']}, Ultra Gelişmiş Asistan")

    # Output text area
    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, width=80, height=25, bg="#333", fg="#0F0", font=("Consolas", 10))
    output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Input frame
    input_frame = tk.Frame(root)
    input_frame.pack(padx=10, pady=5, fill=tk.X)

    input_entry = tk.Entry(input_frame, width=60, font=("Consolas", 10))
    input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    input_entry.bind("<Return>", lambda event=None: send_command()) # Bind Enter key

    send_button = tk.Button(input_frame, text="Gönder", command=send_command, bg="#007bff", fg="white", font=("Arial", 9, "bold"))
    send_button.pack(side=tk.RIGHT, padx=5)

    # Control frame
    control_frame = tk.Frame(root)
    control_frame.pack(padx=10, pady=5, fill=tk.X)

    # Model selection dropdown
    model_var = tk.StringVar(root)
    model_var.set(current_llm) # initial value
    ollama_list_models() # Populate LLM_MODELS with available Ollama models
    model_dropdown = tk.OptionMenu(control_frame, model_var, *LLM_MODELS, command=set_llm_model)
    model_dropdown.config(text="Model Seç", bg="#6c757d", fg="white", font=("Arial", 9, "bold"))
    model_dropdown.pack(side=tk.LEFT, padx=5)
    model_var.trace("w", set_llm_model) # Update when model_var changes

    # GGUF model ekle button
    gguf_button = tk.Button(control_frame, text="GGUF Model Ekle", command=select_gguf_file, bg="#28a745", fg="white", font=("Arial", 9, "bold"))
    gguf_button.pack(side=tk.LEFT, padx=5)

    # Toggle speech button
    speech_button = tk.Button(control_frame, text="Ses Aç/Kapa", command=toggle_speech, bg="#ffc107", fg="black", font=("Arial", 9, "bold"))
    speech_button.pack(side=tk.LEFT, padx=5)

    # Help button
    help_button = tk.Button(control_frame, text="Yardım", command=lambda: update_output(help_menu()), bg="#17a2b8", fg="white", font=("Arial", 9, "bold"))
    help_button.pack(side=tk.LEFT, padx=5)

    # Exit button
    exit_button = tk.Button(control_frame, text="Çıkış", command=root.quit, bg="#dc3545", fg="white", font=("Arial", 9, "bold"))
    exit_button.pack(side=tk.RIGHT, padx=5)

    update_output(f"{user_profile['name']}, Ultra Gelişmiş Asistan'a Hoşgeldin!")
    update_output("Yardım için 'yardım' yazabilirsin veya Yardım butonuna basabilirsin.")
    speak("Ultra Gelişmiş Asistan'a hoşgeldin!")

    root.mainloop()

def toggle_speech():
    global ENABLE_SPEECH
    if VOICE_MODULES:
        ENABLE_SPEECH = not ENABLE_SPEECH
        status = "açıldı" if ENABLE_SPEECH else "kapatıldı"
        update_output(f"Sesli yanıt modu {status}.")
    else:
        update_output("Sesli mod için gerekli modüller (pyttsx3, gtts, playsound) eksik.")

def main():
    load_profile()
    load_aliases()
    load_macros()
    load_history()
    global plugins
    plugins = load_plugins() # Load plugins once at startup
    setup_gui()

if __name__ == "__main__":
    main()
