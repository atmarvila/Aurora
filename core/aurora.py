import sys
import os # Importa OS
import yaml  # Importa a biblioteca PyYAML para ler o arquivo YAML
import speech_recognition as srcd  # Importa speech_recognition
from firebase_admin import storage  # Importa o módulo de storage do Firebase

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.responses import get_greeting_response  # Ajuste a importação com caminho absoluto

class AuroraAI:
    def __init__(self):
        # Inicializa o reconhecedor de fala
        self.recognizer = srcd.Recognizer()

        # Carrega o arquivo YAML
        self.intent_actions = self.load_intent_actions()

    def load_intent_actions(self):
        """Carrega o arquivo intent_actions.yaml e retorna os dados"""
        yaml_path = os.path.join(os.path.dirname(__fsile__), '../data/intent_actions.yaml')
        with open(yaml_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

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

    # Função para executar comandos baseados no texto reconhecido
    def execute_command(self, recognized_text, audio=None):
        # Normaliza o texto reconhecido
        normalized_text = self.normalize_text(recognized_text)

        # Checa as ações no intent_actions.yaml
        for action, details in self.intent_actions['actions'].items():
            phrases = details['triggers']['phrases']
            if any(phrase in normalized_text for phrase in phrases):
                function_name = details['function']
                
                # Chama a função correspondente
                command_function = getattr(self, function_name, None)
                if command_function:
                    print(f"Aurora: Executando a função '{function_name}' para a ação '{action}'")
                    if function_name == "register_collaborator":
                        command_function(audio, recognized_text)  # Passa os argumentos necessários
                    else:
                        command_function()  # Executa a função sem argumentos adicionais
                    return
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

    # Exemplo de funções que devem existir para cada ação no intent_actions.yaml
    def register_timekeeping(self):
        print("Aurora: Registro de ponto realizado.")

    def recognize_registered_voice(self):
        print("Aurora: Verificando voz registrada.")

    def register_client(self):
        print("Aurora: Registrando novo cliente.")

    def deal_of_day(self):
        print("Aurora: A promoção do dia é...")

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.recognize_speech()