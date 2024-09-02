import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, storage
import speechbrain as sb
from speechbrain.inference import SpeakerRecognition
import speech_recognition as srcd
from datetime import datetime
import sys

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.audio_utils import save_audio_wav, load_audio_with_librosa
from reco import AuroraAI  # Importa a classe AuroraAI

# Inicialize o Firebase e o Bucket
def initialize_firebase():
    cred = credentials.Certificate('/Users/pels/Downloads/sevent.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'sevent-7197f.appspot.com'
    })

# Função para fazer upload de áudio no Firebase Storage
def upload_to_firebase(local_file, bucket_path):
    bucket = storage.bucket()
    blob = bucket.blob(bucket_path)
    blob.upload_from_filename(local_file)
    print(f"Upload do arquivo {local_file} para {bucket_path} concluído com sucesso.")

# Inicializa o modelo de reconhecimento de fala e reconhecimento de voz
speaker_rec_model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")
recognizer = srcd.Recognizer()

# Função para capturar e salvar o áudio em formato WAV
def listen_and_save(prompt="Diga algo:", lang="pt-BR"):
    with srcd.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print(prompt)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Ajustes de tempo

        try:
            recognized_text = recognizer.recognize_google(audio, language=lang).lower()
            print(f"Texto reconhecido: {recognized_text}")
            return recognized_text, audio
        except srcd.UnknownValueError:
            print("Aurora: Não consegui entender o que você disse.")
            return None, None
        except srcd.RequestError as e:
            print(f"Aurora: Erro no serviço de reconhecimento de voz: {e}")
            return None, None

# Função para reconhecer vozes registradas no Firebase Storage
def recognize_registered_voice(temp_audio_path):
    bucket = storage.bucket()
    folder_path = "Bistek/Employees/"
    blobs = bucket.list_blobs(prefix=folder_path)

    for blob in blobs:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            try:
                signal_x, sr_x = load_audio_with_librosa(temp_file.name)  # Usando a função importada
                signal_y, sr_y = load_audio_with_librosa(temp_audio_path)  # Usando a função importada
                
                # Usando a função correta verify_batch do SpeechBrain
                verification_score, prediction = speaker_rec_model.verify_batch(signal_x, signal_y)
                print(f"Score de Verificação: {verification_score}, Predição: {prediction}")
                if prediction:
                    return True, os.path.basename(blob.name).replace('.wav', '')
            finally:
                temp_file.close()
                os.remove(temp_file.name)  # Remova o arquivo temporário após o uso
    
    return False, None

# Função principal para o fluxo de conversação
def recognize_speech():
    temp_oi_aurora_path = None
    aurora = AuroraAI()  # Instancia a classe AuroraAI

    while True:
        command, oi_aurora_audio = listen_and_save(prompt="Diga 'Oi Aurora' para começar:")
        if command and "oi aurora" in command:
            temp_dir = tempfile.gettempdir()
            temp_oi_aurora_path = os.path.join(temp_dir, "temp_oi_aurora.wav")
            save_audio_wav(oi_aurora_audio.get_wav_data(), temp_oi_aurora_path)

            # Verificar no Firebase Storage se o áudio "Oi Aurora" corresponde a algum áudio registrado
            recognized, user_name = recognize_registered_voice(temp_oi_aurora_path)

            if recognized:
                print(f"Aurora: Bem-vindo novamente, {user_name.title()}!")
            else:
                print("Aurora: Olá, você ainda não está cadastrado. Vamos iniciar o seu cadastro.")
                aurora.register_collaborator(oi_aurora_audio, command)  # Chama a função na instância da classe
            break

    user_response, new_audio = listen_and_save(prompt="Você: ")

    if user_response and "cadastramento de colaborador" in user_response:
        aurora.register_collaborator(oi_aurora_audio, command)
    elif user_response and new_audio:
        temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")
        save_audio_wav(new_audio.get_wav_data(), temp_audio_path)

        recognized, user_name = recognize_registered_voice(temp_audio_path)

        if recognized:
            print(f"Aurora: Bem-vindo novamente, {user_name.title()}!")
        else:
            print("Aurora: Você ainda não está cadastrado.")
    else:
        print("Aurora: Desculpe, não entendi sua solicitação.")

    if temp_oi_aurora_path and os.path.exists(temp_oi_aurora_path):
        os.remove(temp_oi_aurora_path)

if __name__ == "__main__":
    initialize_firebase()
    recognize_speech()