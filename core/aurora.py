import sys
import os
import speech_recognition as srcd  # Importa speech_recognition
from firebase_admin import storage  # Importa o módulo de storage do Firebase
from responses import get_greeting_response  # Importa a função de resposta

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp_processor import nlp_processor  # Importa o processador NLP
from command_map import employee_map  # Importa o mapa de comandos

class AuroraAI:
    def __init__(self):
        # Inicializa o reconhecedor de fala
        self.recognizer = srcd.Recognizer()

    def normalize_text(self, text):
        text = text.lower()
        # Normaliza pluralizações comuns
        text = text.replace("colaboradores", "colaborador")
        text = text.replace("clientes", "cliente")
        text = text.replace("promoções", "promoção")
        # Adicione mais regras de normalização conforme necessário
        return text

    def handle_greeting(self):
        # Função para lidar com saudações como "Oi Aurora"
        response = get_greeting_response()
        print(f"Aurora: {response}")

    # Função para reconhecer voz registrada
    def recognize_registered_voice(self, registered_audio_path, new_audio_path):
        # Código para reconhecer voz registrada
        pass

    # Função para executar comandos baseados no texto reconhecido
    def execute_command(self, recognized_text, audio=None):
        # Normaliza o texto reconhecido
        normalized_text = self.normalize_text(recognized_text)

        # Checa se é uma saudação
        if "oi aurora" in normalized_text:
            self.handle_greeting()
            return

        # Usa o processador NLP para encontrar o comando apropriado
        command_function_name = nlp_processor(normalized_text, employee_map)
        if command_function_name:
            # Obtém a função correspondente ao comando encontrado
            command_function = getattr(self, command_function_name, None)
            if command_function:
                if command_function_name == "register_collaborator":
                    command_function(audio, recognized_text)  # Passa os argumentos necessários
                else:
                    command_function()  # Executa a função sem argumentos adicionais
            else:
                print("Aurora: Desculpe, não consigo executar esse comando.")
        else:
            print("Aurora: Comando não reconhecido. Tente novamente.")

    def recognize_speech(self):
        while True:
            recognized_text, audio = self.listen_and_save(prompt="Você: ")  # Obtém o texto reconhecido e o áudio
            if recognized_text:
                # Se o usuário disser "tchau", a sessão será encerrada
                if "tchau" in recognized_text or "encerrar" in recognized_text:
                    print("Aurora: Até logo!")
                    break

                self.execute_command(recognized_text, audio)  # Passa o texto e o áudio para execute_command

    def listen_and_save(self, prompt="Diga algo:", lang="pt-BR"):
        with srcd.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print(prompt)
            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Ajustes de tempo

            try:
                recognized_text = self.recognizer.recognize_google(audio, language=lang).lower()
                print(f"Texto reconhecido: {recognized_text}")
                return recognized_text, audio
            except srcd.UnknownValueError:
                print("Aurora: Não consegui entender o que você disse.")
                return None, None
            except srcd.RequestError as e:
                print(f"Aurora: Erro no serviço de reconhecimento de voz: {e}")
                return None, None

    def upload_to_firebase(self, local_file, bucket_path):
        bucket = storage.bucket()
        blob = bucket.blob(bucket_path)
        try:
            blob.upload_from_filename(local_file)
            print(f"Upload do arquivo {local_file} para {bucket_path} concluído com sucesso.")
        except Exception as e:
            print(f"Erro ao fazer upload para o Firebase: {e}")

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.recognize_speech()