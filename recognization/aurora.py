import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, storage
import speechbrain as sb
from speechbrain.inference import SpeakerRecognition
import speech_recognition as srcd
from datetime import datetime
import wave
import librosa
import torch

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

# Carrega o template JSON de cadastro de colaboradores
def load_employee_template():
    with open('templates/employees.json', 'r') as file:
        return json.load(file)

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

# Função para salvar áudio como um arquivo WAV
def save_audio_wav(audio_data, file_path):
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_data)

# Função para registrar um colaborador
def register_collaborator(name_audio, name_text):
    folder_path = tempfile.gettempdir()

    # Carrega o template JSON
    employee_template = load_employee_template()

    # Inicializa uma lista para armazenar todos os áudios capturados
    combined_audio_data = []

    # Ordem das perguntas
    order_of_questions = [
        "name", "last_name", "role", "DOB", "supermarket_id", 
        "document_type", "document", "notification", "contact_number", "service_company"
    ]

    # Coleta as informações do colaborador baseado no JSON
    employee_data = {
        "modication_date": datetime.now().isoformat(),
        "register_date": datetime.now().isoformat()
    }
    document_number = None

    for field in order_of_questions:
        attributes = employee_template['collaborator_registration']['fields'][field]
        print(f"Aurora: Por favor, informe {attributes['label']}.")
        response, audio = listen_and_save()
        if response:
            if attributes['type'] == 'timestamp':
                employee_data[field] = datetime.now().isoformat()
            elif attributes['type'] == 'boolean':
                employee_data[field] = True if response.lower() in ['sim', 'yes', 'true'] else False
            else:
                employee_data[field] = response

            # Armazena o áudio capturado
            combined_audio_data.append(audio.get_wav_data())

            # Captura o número do documento para nomear o arquivo
            if field == "document":
                document_number = response
        else:
            print(f"Aurora: Campo {attributes['label']} não foi preenchido corretamente.")
            return

    if document_number:
        # Combina todos os áudios em um único arquivo WAV
        final_audio_path = os.path.join(folder_path, f"{document_number}.wav")
        with wave.open(final_audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            for audio_data in combined_audio_data:
                wf.writeframes(audio_data)

        # Upload do áudio combinado para o Firebase
        upload_to_firebase(final_audio_path, f"Bistek/Employees/{document_number}.wav")

        print(f"Aurora: Cadastro concluído. Áudio salvo como {document_number}.wav")
    else:
        print("Aurora: Não foi possível registrar o colaborador, número de documento não fornecido.")

# Função para carregar o áudio com librosa
def load_audio_with_librosa(file_path):
    signal, sr = librosa.load(file_path, sr=None)
    return torch.tensor(signal).unsqueeze(0), sr  # Converte para tensor e adiciona uma dimensão extra

# Função para reconhecer vozes registradas no Firebase Storage
def recognize_registered_voice(temp_audio_path):
    bucket = storage.bucket()
    folder_path = "Bistek/Employees/"
    blobs = bucket.list_blobs(prefix=folder_path)

    for blob in blobs:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            try:
                signal_x, sr_x = load_audio_with_librosa(temp_file.name)
                signal_y, sr_y = load_audio_with_librosa(temp_audio_path)
                
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
                register_collaborator(oi_aurora_audio, command)
            break

    user_response, new_audio = listen_and_save(prompt="Você: ")

    if user_response and "cadastramento de colaborador" in user_response:
        register_collaborator(oi_aurora_audio, command)
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