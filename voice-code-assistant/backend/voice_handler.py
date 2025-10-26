import speech_recognition as sr
import pyttsx3

def speak(text):
    """Convert text to speech"""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    print(f"🔊 Spoke: {text}")

def listen():
    """Listen for a voice command"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎤 Listening for voice command... (speak now)")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"🗣 Recognized command: {command}")
        return command
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Error from speech recognition service: {e}")
        return None
