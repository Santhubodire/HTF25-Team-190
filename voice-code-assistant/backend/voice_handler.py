import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import tempfile
import pyttsx3

def listen():
    """
    Records audio from the user's microphone using sounddevice,
    saves it temporarily as a WAV file, and converts it to text
    using Google's speech recognition API.
    """
    recognizer = sr.Recognizer()
    duration = 5  # seconds to record (you can adjust this)

    try:
        print("🎤 Listening for voice command... (speak now)")
        sample_rate = 16000

        # Record audio using sounddevice
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()

        # Save the recorded audio to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio_data, sample_rate)
            tmp_filename = tmpfile.name

        # Convert audio to text
        with sr.AudioFile(tmp_filename) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        print(f"🗣 Recognized command: {text}")
        return text

    except sr.UnknownValueError:
        print("❌ Could not understand the audio.")
        return "Could not understand the command."
    except sr.RequestError as e:
        print(f"⚠️ Speech Recognition service error: {e}")
        return "Speech recognition service unavailable."
    except Exception as e:
        print(f"⚠️ Error during listening: {e}")
        return "Error capturing audio."

def speak(text):
    """
    Converts text to speech output using pyttsx3.
    """
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        print(f"🔊 Spoke: {text}")
    except Exception as e:
        print(f"⚠️ Text-to-speech error: {e}")
