import speech_recognition as sr
import pyttsx3

def recognize_speech(lang="tr-TR"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Konuşmanızı bekliyorum...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language=lang)
        print(f"Algılanan: {text}")
        return text
    except sr.UnknownValueError:
        return "Sizi anlayamadım."
    except sr.RequestError as e:
        return f"Servis hatası: {e}"

def speak_text(text, engine_name="default"):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
