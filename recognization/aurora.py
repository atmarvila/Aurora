import os
import tempfile
import speechbrain as sb
from speechbrain.inference import SpeakerRecognition
import speech_recognition as srcd

# Initialize the SpeechBrain speaker recognition model
speaker_rec_model = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

# Initialize the recognizer for basic speech-to-text
recognizer = srcd.Recognizer()

# Function to capture and save the audio in WAV format only
def listen_and_save(prompt="Diga algo:", lang="pt-BR"):
    with srcd.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print(prompt)
        audio = recognizer.listen(source)

        try:
            recognized_text = recognizer.recognize_google(audio, language=lang).lower()
            print(f"Texto reconhecido: {recognized_text}")  # Adiciona o texto reconhecido para depuração
            return recognized_text, audio
        except srcd.UnknownValueError:
            print("Aurora: Não consegui entender o que você disse.")
            return None, None
        except srcd.RequestError as e:
            print(f"Aurora: Erro no serviço de reconhecimento de voz: {e}")
            return None, None

# Function to register a collaborator
def register_collaborator(name_audio, name_text):
    formatted_name = name_text.replace(" ", "_")
    folder_path = r"C:\Users\rmarv\OneDrive\Área de Trabalho\Sevent\Colaboradores_Reconhecimento"
    os.makedirs(folder_path, exist_ok=True)
    
    # Save the "Oi Aurora" audio
    oi_aurora_path = os.path.join(folder_path, f"{formatted_name}_oi_aurora.wav")
    with open(oi_aurora_path, "wb") as f:
        f.write(name_audio.get_wav_data())
    
    # Capture the collaborator's full name
    print("Aurora: Por favor, diga seu nome completo.")
    name, audio = listen_and_save()
    if name and audio:
        file_path = os.path.join(folder_path, f"{formatted_name}.wav")

        # Save the audio as WAV
        with open(file_path, "wb") as f:
            f.write(audio.get_wav_data())

        print(f"Aurora: Cadastro concluído {name.capitalize()}. Até logo!")
        print(f"Áudio salvo em {file_path}")
        return file_path, oi_aurora_path  # Retorna os caminhos dos arquivos salvos para depuração

# Function to recognize registered voices
def recognize_registered_voice(registered_audio_path, new_audio_path):
    verification_score, prediction = speaker_rec_model.verify_files(registered_audio_path, new_audio_path)
    
    # Exibe o score e a predição para depuração
    print(f"Score de Verificação: {verification_score}, Predição: {prediction}")
    
    return verification_score, prediction

# Main function for the conversation flow
def recognize_speech():
    temp_audio_path = None  # Inicializa a variável para evitar problemas de escopo
    temp_oi_aurora_path = None  # Inicializa a variável para evitar problemas de escopo
    
    # Wait for the user to start with "Oi Aurora"
    while True:
        command, oi_aurora_audio = listen_and_save(prompt="Diga 'Oi Aurora' para começar:")
        if command and "oi aurora" in command:
            # Salva o áudio temporário "Oi Aurora" em um diretório seguro
            temp_dir = tempfile.gettempdir()  # Diretório temporário seguro
            temp_oi_aurora_path = os.path.join(temp_dir, "temp_oi_aurora.wav")
            with open(temp_oi_aurora_path, "wb") as f:
                f.write(oi_aurora_audio.get_wav_data())

            # Check if "Oi Aurora" matches any registered "Oi Aurora"
            folder_path = r"C:\Users\rmarv\OneDrive\Área de Trabalho\Sevent\Colaboradores_Reconhecimento"
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and "oi_aurora" in f]

            recognized = False
            for file in files:
                registered_audio_path = os.path.join(folder_path, file)
                score, prediction = recognize_registered_voice(registered_audio_path, temp_oi_aurora_path)

                if prediction:  # If "Oi Aurora" is recognized
                    # Extract and format the user's name
                    user_name = os.path.splitext(file.replace('_oi_aurora', '').replace('_', ' ').title())[0]
                    print(f"Aurora: Bem-vindo novamente, {user_name}!")
                    recognized = True
                    break
            
            if not recognized:
                print("Aurora: Olá, como posso te ajudar hoje?")
            break

    # Continue from the user's response
    user_response, new_audio = listen_and_save(prompt="Você: ")

    if user_response and "cadastramento de colaborador" in user_response:
        register_collaborator(oi_aurora_audio, command)
    elif user_response and new_audio:
        temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")
        with open(temp_audio_path, "wb") as f:
            f.write(new_audio.get_wav_data())

        # Attempt to recognize if the user is already registered
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and "oi_aurora" not in f]

        recognized = False
        for file in files:
            registered_audio_path = os.path.join(folder_path, file)
            score, prediction = recognize_registered_voice(registered_audio_path, temp_audio_path)

            if prediction:  # Se a voz for reconhecida
                print(f"Aurora: Bem-vindo novamente, {file.replace('_', ' ').replace('.wav', '').title()}!")
                recognized = True
                break

        if not recognized:
            print("Aurora: Você ainda não está cadastrado.")
    else:
        print("Aurora: Desculpe, não entendi sua solicitação.")

    # Remove os arquivos de áudio temporários
    if temp_oi_aurora_path and os.path.exists(temp_oi_aurora_path):
        os.remove(temp_oi_aurora_path)
    if temp_audio_path and os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

# Call the function to start speech recognition
recognize_speech()