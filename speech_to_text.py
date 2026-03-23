import os
import tempfile
from pydub import AudioSegment
import speech_recognition as sr

_recognizer = sr.Recognizer()

def _convert_to_wav(source_path: str, target_path: str):
    audio = AudioSegment.from_file(source_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(target_path, format="wav")

def transcribe_wav_path(wav_path: str) -> str:
    try:
        with sr.AudioFile(wav_path) as source:
            audio = _recognizer.record(source)
        return _recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError as e:
        return f"Speech recognition request failed: {e}"
    except Exception as e:
        return f"Error transcribing audio: {e}"

def transcribe_uploaded_file(uploaded_file) -> str:
    suffix = os.path.splitext(uploaded_file.name)[1].lower() or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_src:
        tmp_src.write(uploaded_file.getbuffer())
        tmp_src_path = tmp_src.name

    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_wav_path = tmp_wav.name
    tmp_wav.close()

    try:
        _convert_to_wav(tmp_src_path, tmp_wav_path)
        return transcribe_wav_path(tmp_wav_path)
    finally:
        try: os.remove(tmp_src_path)
        except: pass
        try: os.remove(tmp_wav_path)
        except: pass
