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

# Ekstra modüller (isteğe bağlı)
try:
    import psutil
except ImportError:
    psutil = None

# winshell modülü (önerilen ve daha sağlam .lnk okuma için)
try:
    import winshell
except ImportError:
    winshell = None
    print("Uyarı: 'winshell' modülü bulunamadı. .lnk dosyalarının hedefleri doğru okunamayabilir. 'pip install winshell' ile yüklemeniz önerilir.")


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
LLM_MODELS = ["llama3", "mistral", "phi3"]
DEFAULT_LLM_MODEL = "llama3"
ENABLE_SPEECH = False
MAX_HISTORY = 40
PLUGIN_FOLDER = "plugins"
PROFILE_FILE = "user_profile.json"
ALIASES_FILE = "aliases.json"
MACRO_FILE = "macros.json"
CHAT_HISTORY_FILE = "chat_history.txt"
PROGRAM_LIST_FILE = "found_programs.json" # Kullanıcı programları için dosya
SYSTEM_PROGRAM_LIST_FILE = "system_programs.json" # Yeni: Sistem programları için dosya

PROGRAM_SEARCH_PATHS = [ # Kullanıcı programları için aranacak temel yollar
    os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files")),
    os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")),
    os.path.join(os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming")), "Microsoft\\Windows\\Start Menu\\Programs"),
    os.path.join(os.environ.get("ALLUSERSPROFILE", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
    os.path.expanduser("~\\Desktop")
]

SYSTEM_PROGRAM_SEARCH_PATHS = [ # Yeni: Sistem uygulamaları için aranacak yollar
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32"),
    os.path.join(os.environ.get("WINDIR", "C:\\Windows")),
]


# === GLOBAL DURUM ===
chat_history = []
user_profile = {}
aliases = {}
macros = {}
system_os = platform.system()
current_llm = DEFAULT_LLM_MODEL
found_programs = {} # Bulunan kullanıcı programlarını saklayacak sözlük
system_programs = {} # Yeni: Bulunan sistem programlarını saklayacak sözlük

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
                role, content = line.strip().split(":", 1)
                chat_history.append({"role": role, "content": content})

def save_found_programs():
    """Bulunan kullanıcı programlar listesini JSON dosyasına kaydeder."""
    with open(PROGRAM_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(found_programs, f, indent=2, ensure_ascii=False)

def load_found_programs():
    """Kaydedilmiş kullanıcı programlar listesini yükler."""
    global found_programs
    if os.path.exists(PROGRAM_LIST_FILE):
        with open(PROGRAM_LIST_FILE, "r", encoding="utf-8") as f:
            found_programs = json.load(f)
    else:
        found_programs = {}

def save_system_programs(): # Yeni fonksiyon
    """Bulunan sistem programlar listesini JSON dosyasına kaydeder."""
    with open(SYSTEM_PROGRAM_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(system_programs, f, indent=2, ensure_ascii=False)

def load_system_programs(): # Yeni fonksiyon
    """Kaydedilmiş sistem programlar listesini yükler."""
    global system_programs
    if os.path.exists(SYSTEM_PROGRAM_LIST_FILE):
        with open(SYSTEM_PROGRAM_LIST_FILE, "r", encoding="utf-8") as f:
            system_programs = json.load(f)
    else:
        system_programs = {}

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
        return input("Komutunuzu yazın: ")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Dinliyorum...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio, language="tr-TR")
    except Exception:
        print("Ses algılanamadı, lütfen tekrar deneyin.")
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
        # "ollama create <model_name> --file Modelfile"
        result = subprocess.run(
            ["ollama", "create", model_name, "--file", "Modelfile"],
            capture_output=True, text=True, timeout=1200
        )
        os.chdir(prev_dir)
        if result.returncode == 0:
            if model_name not in LLM_MODELS:
                LLM_MODELS.append(model_name)
            return f"Model {model_name} başarıyla eklendi ve Ollama ile kullanılabilir!"
        else:
            return f"Ollama create hatası:\n{result.stderr}"
    except Exception as e:
        return f"Ollama model ekleme hatası: {e}"

def ollama_list_models():
    """
    Ollama'da kayıtlı modelleri listeler.
    """
    if not shutil.which("ollama"):
        return "Ollama yüklü değil veya PATH'de değil!"
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
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
                print(f"Eklenti yüklenemedi: {modname} ({e})")
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
        return f"'{src}' -> '{dst}' taşındı."
    except Exception as e:
        return f"Hata: {e}"

def delete_file(filepath):
    try:
        os.remove(filepath)
        return f"'{filepath}' silindi."
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

# === PROGRAM ARAMA VE YÖNETİMİ ===
def get_lnk_target_winshell(lnk_path):
    """Winshell kullanarak .lnk dosyasının hedefini alır."""
    if not winshell:
        return None
    try:
        shortcut = winshell.shortcut(lnk_path)
        target = shortcut.path
        if shortcut.arguments:
            target += f" {shortcut.arguments}"
        return target
    except Exception as e:
        return None

def search_programs(search_paths, target_dict, file_type="user"):
    """Belirtilen yollarda .exe, .com, .bat, .cmd ve .lnk (kullanıcı için) programlarını arar ve belirtilen sözlüğe kaydeder."""
    print(f"{'Sistem' if file_type == 'system' else 'Kullanıcı'} programları aranıyor... Bu biraz zaman alabilir.")
    found_count = 0
    # Önemli: Sistem dizinlerinde çok fazla dosya olabilir.
    # İlk çalıştırmada çok uzun sürmemesi için derinliği sınırlamak faydalı olabilir.
    # Bu örnekte tam dolaşım yapılıyor, dilerseniz bir max_depth parametresi ekleyebilirsiniz.
    
    for path_to_search in search_paths:
        if not os.path.exists(path_to_search):
            continue

        for root, _, files in os.walk(path_to_search):
            # Derinliği sınırlama örneği (isteğe bağlı)
            # current_depth = root.count(os.sep) - path_to_search.count(os.sep)
            # if current_depth > 3: # 3 alt dizinle sınırlama
            #     continue

            for file in files:
                file_path = os.path.join(root, file)
                program_name, ext = os.path.splitext(file)

                # Çalıştırılabilir dosyalar için genel kontrol
                if ext.lower() in (".exe", ".com", ".bat", ".cmd"):
                    # Zaten kaydettiysek ve path aynıysa atla (güncelleme veya tekrar eklemeyi önle)
                    if program_name in target_dict and target_dict[program_name]["path"] == file_path:
                        continue
                    
                    target_dict[program_name] = {
                        "path": file_path,
                        "type": ext.lstrip('.'), # uzantıyı kaydet (exe, com vb.)
                        "last_found": str(datetime.datetime.now())
                    }
                    found_count += 1
                elif ext.lower() == ".lnk" and system_os == "Windows" and file_type == "user":
                    # .lnk dosyalarını sadece kullanıcı programları için işle
                    target_path = None
                    if winshell:
                        target_path = get_lnk_target_winshell(file_path)

                    if target_path and os.path.exists(target_path) and \
                       os.path.splitext(target_path)[1].lower() in (".exe", ".com", ".bat", ".cmd"):
                        
                        if program_name in target_dict and target_dict[program_name].get("original_lnk") == file_path:
                            continue

                        target_dict[program_name] = {
                            "path": target_path, # Hedef yol
                            "type": "lnk",
                            "original_lnk": file_path, # Kısayolun kendisi
                            "last_found": str(datetime.datetime.now())
                        }
                        found_count += 1
    
    if found_count > 0:
        if file_type == "user":
            save_found_programs()
        elif file_type == "system":
            save_system_programs()
        return f"{found_count} yeni {'sistem' if file_type == 'system' else 'kullanıcı'} programı bulundu ve kaydedildi."
    else:
        return f"Yeni {'sistem' if file_type == 'system' else 'kullanıcı'} programı bulunamadı."


def launch_program(program_name):
    """Kaydedilmiş programlardan birini (kullanıcı veya sistem) başlatır."""
    program_name_lower = program_name.lower()

    # Önce kullanıcı programlarında ara
    for name, details in found_programs.items():
        if name.lower() == program_name_lower:
            try:
                # Kısayollar için original_lnk yolunu kullanmak daha güvenli olabilir
                # Çünkü Windows kabuğu .lnk'yi doğru şekilde yorumlar.
                path_to_launch = details.get("original_lnk", details["path"])
                subprocess.Popen([path_to_launch], shell=True)
                return f"'{name}' kullanıcı programı başlatıldı: {path_to_launch}"
            except Exception as e:
                return f"'{name}' kullanıcı programı başlatılırken hata oluştu: {e}"
    
    # Kullanıcı programlarında bulunamazsa, sistem programlarında ara
    for name, details in system_programs.items():
        if name.lower() == program_name_lower:
            try:
                subprocess.Popen([details["path"]], shell=True)
                return f"'{name}' sistem programı başlatıldı: {details['path']}"
            except Exception as e:
                return f"'{name}' sistem programı başlatılırken hata oluştu: {e}"

    return f"'{program_name}' programı bulunamadı. 'program ara' veya 'sistem program ara' komutlarını kullanmayı deneyin."


def list_found_programs():
    """Kaydedilmiş kullanıcı programlarını listeler."""
    if not found_programs:
        user_output = "Henüz kayıtlı bir kullanıcı programı bulunamadı. 'program ara' komutunu kullanın."
    else:
        user_output = ["--- Kayıtlı Kullanıcı Programları ---"]
        for name, details in found_programs.items():
            program_type = "Kısayol" if details['type'] == 'lnk' else details['type'].upper()
            output.append(f"- {name} ({program_type}): {details['path']}")
        user_output.append("-------------------------")
        user_output = "\n".join(user_output)
    return user_output

def list_system_programs(): # Yeni fonksiyon
    """Kaydedilmiş sistem programlarını listeler."""
    if not system_programs:
        system_output = "Henüz kayıtlı bir sistem programı bulunamadı. 'sistem program ara' komutunu kullanın."
    else:
        system_output = ["--- Kayıtlı Sistem Programları ---"]
        for name, details in system_programs.items():
            program_type = details['type'].upper()
            output.append(f"- {name} ({program_type}): {details['path']}")
        system_output.append("-------------------------")
        system_output = "\n".join(system_output)
    return system_output

def list_all_programs(): # Yeni fonksiyon
    """Tüm kaydedilmiş programları (kullanıcı ve sistem) listeler."""
    user_list = list_found_programs()
    system_list = list_system_programs()
    return f"{user_list}\n\n{system_list}"


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
    else:
        return "Makro yok."

# === KOMUTLAR ===
def help_menu():
    menu = (
        "\n--- Komutlar ---\n"
        "ai: <soru>         - Soru/istek için LLM'ye danış\n"
        "dosya oku <yol>    - Dosya içeriğini göster\n"
        "dosya yaz <yol>    - Dosyaya yaz\n"
        "listele <yol>      - Klasör içeriğini göster\n"
        "çalıştır <komut>   - Terminal/komut çalıştırır\n"
        "program ara        - Kullanıcı .lnk ve .exe programlarını arar ve kaydeder\n"
        "sistem program ara - Sistemdeki .exe programlarını arar ve kaydeder\n"
        "program listele    - Kaydedilmiş kullanıcı programlarını listeler\n"
        "sistem program listele - Kaydedilmiş sistem programlarını listeler\n"
        "tüm programları listele - Tüm kayıtlı programları listeler\n"
        "program başlat <ad> - Kayıtlı programı başlatır (kullanıcı veya sistem)\n"
        "sistem bilgi       - Sistem bilgisi verir\n"
        "prosesler          - Aktif prosesleri listeler\n"
        "sonlandır <pid>    - Proses sonlandır\n"
        "ara <kelime>       - İnternette arama\n"
        "ssh <host> <user> <password> <cmd> - Uzaktan komut çalıştır\n"
        "alias ekle <ad> <komut>\n"
        "alias sil <ad>\n"
        "alias çalıştır <ad>\n"
        "makro ekle <ad>\n"
        "makro sil <ad>\n"
        "makro çalıştır <ad>\n"
        "eklentiler         - Yüklü eklentileri listeler\n"
        "kullan <eklenti> <veri> - Eklenti çalıştır\n"
        "model ekle <gguf_yolu> <model_adı> - GGUF dosyasından Ollama modeli ekle\n"
        "model list         - Ollama'daki modelleri listeler\n"
        "model <ad>         - LLM modelini değiştir\n"
        "profil             - Kullanıcı profili göster\n"
        "ses aç / ses kap   - Sesli cevap modunu aç/kapat\n"
        "geçmiş             - Son sohbet geçmişi\n"
        "çıkış              - Programı sonlandırır\n"
        "----------------\n"
    )
    return menu

# === ANA DÖNGÜ ===
def main():
    global ENABLE_SPEECH
    global current_llm
    load_profile()
    load_aliases()
    load_macros()
    load_history()
    load_found_programs()
    load_system_programs() # Yeni: Sistem program listesini yükle
    plugins = load_plugins()
    print(f"{user_profile['name']}, Ultra Gelişmiş Asistan'a Hoşgeldin!")
    print("Yardım için 'yardım' yazabilirsin.")
    speak("Ultra Gelişmiş Asistan'a hoşgeldin!")
    while True:
        try:
            if ENABLE_SPEECH and VOICE_MODULES:
                print("\nKomutunuzu (veya 'yardım') söyleyin:")
            else:
                print("\nKomutunuzu yazın (veya 'yardım'):")
            user_input = listen().strip()
            if not user_input:
                continue
            chat_history.append({"role": "user", "content": user_input})
            if user_input.lower() in ("çıkış", "exit", "quit"):
                print("Görüşmek üzere!")
                speak("Görüşmek üzere!")
                save_history()
                save_found_programs()
                save_system_programs() # Yeni: Sistem program listesini kaydet
                break
            elif user_input.lower() in ("yardım", "help"):
                print(help_menu())
            # --- Program Arama ve Yönetimi Komutları ---
            elif user_input.lower() == "program ara":
                print(search_programs(PROGRAM_SEARCH_PATHS, found_programs, file_type="user"))
            elif user_input.lower() == "sistem program ara":
                # Kapsamlı bir sistem araması ilk başta çok uzun sürebilir.
                # Yüksek sayıda dosya olduğu için sadece .exe uzantılarını kontrol etmesi daha hızlı olabilir.
                # os.walk zaten bunu yapıyor, ancak System32 gibi dizinlerin derinliği büyük olabilir.
                print(search_programs(SYSTEM_PROGRAM_SEARCH_PATHS, system_programs, file_type="system"))
            elif user_input.lower().startswith("program başlat"):
                program_to_launch = user_input[15:].strip()
                if program_to_launch:
                    print(launch_program(program_to_launch))
                else:
                    print("Lütfen başlatmak istediğiniz programın adını belirtin. Kullanım: program başlat <program_adı>")
            elif user_input.lower() == "program listele":
                print(list_found_programs())
            elif user_input.lower() == "sistem program listele":
                print(list_system_programs())
            elif user_input.lower() == "tüm programları listele":
                print(list_all_programs())
            # --- Mevcut Komutlar devam ediyor ---
            elif user_input.lower().startswith("model ekle"):
                parts = user_input.split()
                if len(parts) >= 4:
                    _, _, gguf_path, model_name = parts[:4]
                    print(ollama_create_model_from_gguf(gguf_path, model_name))
                else:
                    print("Kullanım: model ekle <gguf_yolu> <model_adı>")
            elif user_input.lower().startswith("model list"):
                print(ollama_list_models())
            # --- Var olan model seçme ---
            elif user_input.lower().startswith("model"):
                _, model = user_input.split()
                if model in LLM_MODELS:
                    current_llm = model
                    print(f"LLM modeli {model} olarak ayarlandı.")
                else:
                    print(f"Desteklenen modeller: {', '.join(LLM_MODELS)}")
            elif user_input.lower().startswith("ai:"):
                prompt = user_input[3:].strip()
                reply = ask_llm(prompt, chat_history, current_llm)
                print(f"AI: {reply}")
                speak(reply)
                chat_history.append({"role": "assistant", "content": reply})
            elif user_input.lower().startswith("dosya oku"):
                path = user_input[9:].strip()
                print(read_file(path))
            elif user_input.lower().startswith("dosya yaz"):
                path = user_input[9:].strip()
                print("Yazmak istediğiniz içeriği girin (bitirmek için tek satırda 'bitti' yazın):")
                lines = []
                while True:
                    line = input()
                    if line.strip().lower() == "bitti":
                        break
                    lines.append(line)
                print(write_file(path, "\n".join(lines)))
            elif user_input.lower().startswith("listele"):
                path = user_input[7:].strip() or "."
                files = list_files(path)
                print("\n".join(files))
            elif user_input.lower().startswith("çalıştır"):
                cmd = user_input[9:].strip()
                print(run_shell_command(cmd))
            elif user_input.lower().startswith("ara"):
                q = user_input[3:].strip()
                print(web_search(q))
            elif user_input.lower() == "sistem bilgi":
                print(get_system_info())
            elif user_input.lower() == "prosesler":
                print(list_processes())
            elif user_input.lower().startswith("sonlandır"):
                pid = user_input[10:].strip()
                print(kill_process(pid))
            elif user_input.lower().startswith("ssh"):
                parts = user_input.split()
                if len(parts) >= 5:
                    host, user, password, cmd = parts[1], parts[2], parts[3], " ".join(parts[4:])
                    print(ssh_run_cmd(host, user, password, cmd))
                else:
                    print("Kullanım: ssh <host> <user> <password> <cmd>")
            elif user_input.lower().startswith("alias ekle"):
                _, _, alias, *command = user_input.split()
                print(add_alias(alias, " ".join(command)))
            elif user_input.lower().startswith("alias sil"):
                _, _, alias = user_input.split()
                print(delete_alias(alias))
            elif user_input.lower().startswith("alias çalıştır"):
                _, _, alias = user_input.split()
                print(run_alias(alias))
            elif user_input.lower().startswith("makro ekle"):
                _, _, name = user_input.split()
                print("Makroya eklenecek komutları girin (bitirmek için tek satırda 'bitti' yazın):")
                commands = []
                while True:
                    cmd = input()
                    if cmd.strip().lower() == "bitti":
                        break
                    commands.append(cmd)
                print(add_macro(name, commands))
            elif user_input.lower().startswith("makro sil"):
                _, _, name = user_input.split()
                print(delete_macro(name))
            elif user_input.lower().startswith("makro çalıştır"):
                _, _, name = user_input.split()
                print(run_macro(name))
            elif user_input.lower() == "eklentiler":
                if plugins:
                    print("Yüklü eklentiler: " + ", ".join(plugins.keys()))
                else:
                    print("Hiç eklenti yüklenmedi.")
            elif user_input.lower().startswith("kullan"):
                parts = user_input.split(maxsplit=2)
                if len(parts) >= 3:
                    plugin, data = parts[1], parts[2]
                    if plugin in plugins:
                        try:
                            result = plugins[plugin](data)
                            print(result)
                        except Exception as e:
                            print(f"Eklenti hatası: {e}")
                    else:
                        print("Eklenti bulunamadı.")
                else:
                    print("Kullanım: kullan <eklenti> <veri>")
            elif user_input.lower() == "profil":
                print(json.dumps(user_profile, indent=2, ensure_ascii=False))
            elif user_input.lower() == "ses aç":
                if VOICE_MODULES:
                    ENABLE_SPEECH = True
                    print("Sesli yanıt modu açıldı.")
                else:
                    print("Sesli mod için gerekli modüller eksik.")
            elif user_input.lower() == "ses kap":
                ENABLE_SPEECH = False
                print("Sesli yanıt modu kapatıldı.")
            elif user_input.lower() == "geçmiş":
                for x in chat_history[-MAX_HISTORY:]:
                    print(f"{x['role']}: {x['content']}")
            else:
                # AI'dan öneri al: komutun ne olduğunu anlamazsa
                prompt = f"Kullanıcı şu isteği verdi: '{user_input}'. Ne yapmak istediğini analiz et, öneri ve komut ver."
                reply = ask_llm(prompt, chat_history, current_llm)
                print(f"AI önerisi: {reply}")
                speak(reply)
                chat_history.append({"role": "assistant", "content": reply})
        except KeyboardInterrupt:
            print("\nKapatılıyor.")
            save_history()
            save_found_programs()
            save_system_programs() # Çıkışta sistem programlarını kaydet
            break
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    main()
