import os

# Temel yapılandırma ayarları

PROJECT_NAME = "Sesli Komut Asistanı"
VERSION = "1.0.0"
DEBUG = True

# Kayıt ve günlükleme ayarları
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "assistant.log")

# Ses ayarları
VOICE_RECOGNITION_LANG = "tr-TR"
VOICE_ENGINE = "default"  # "default" veya ör: "espeak", "sapi5"

# LLM ayarları
LLM_MODEL = "ollama/turkish-model"

# Diğer sistem ayarları
MAX_HISTORY = 10
