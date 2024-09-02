import tempfile
import wave
import librosa
import torch

def save_audio_wav(audio_data, file_path):
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_data)

def load_audio_with_librosa(file_path):
    signal, sr = librosa.load(file_path, sr=None)
    return torch.tensor(signal).unsqueeze(0), sr  # Converte para tensor e adiciona uma dimensão extra