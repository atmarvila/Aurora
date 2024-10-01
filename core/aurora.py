import sys
import os
import yaml
import speech_recognition as srcd
from firebase_admin import storage

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa os módulos de ações das pastas apropriadas
from core.actions.promotion.deal_of_day import deal_of_day
from core.actions.register.register_client import register_client
from core.actions.register.register_employee import CollaboratorRegistration
from core.actions.register.register_timekeeping import register_timekeeping
from core.actions.validation.recognize_registered_voice import recognize_registered_voice

# Importa o processador NLP e as respostas
from core.nlp.nlp_processor import nlp_processor
from core.responses.responses import get_greeting_response


class AuroraAI:
    def __init__(self):
        # Inicializa o reconhecedor de fala
        self.recognizer = srcd.Recognizer()

        # Carrega o arquivo intent_actions.yaml e responses.yaml
        self.intent_actions = self.load_yaml_file('../data/intent_actions.yaml')
        self.responses = self.load_yaml_file('../data/responses.yaml')

        # Instancia a classe CollaboratorRegistration passando a instância de AuroraAI
        self.collaborator_registration = CollaboratorRegistration(self)

        # Dicionário de ações mapeando funções para ações correspondentes
        self.action_map = {
            'register_timekeeping': register_timekeeping,
            'recognize_registered_voice': recognize_registered_voice,
            'register_client': register_client,
            'deal_of_day': deal_of_day,
            'register_collaborator': self.collaborator_registration.register_collaborator
        }

    def load_yaml_file(self, relative_path):
        """Carrega um arquivo YAML e retorna os dados"""
        yaml_path = os.path.join(os.path.dirname(__file__), relative_path)
        with open(yaml_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get_response(self, category, action=None):
        """Obtém uma resposta da categoria especificada"""
        if action and action in self.responses['actions']:
            return self.responses['actions'][action]
        if category in self.responses:
            return self.responses[category][0]
        return self.responses['default_response']

    def normalize_text(self, text):
        text = text.lower()
        text = text.replace("colaboradores", "colaborador")
        text = text.replace("clientes", "cliente")
        text = text.replace("promoções", "promoção")
        return text

    def execute_command(self, recognized_text, audio=None):
        # Normaliza o texto reconhecido
        normalized_text = self.normalize_text(recognized_text)

        # Checa as ações no intent_actions.yaml
        for action, details in self.intent_actions['actions'].items():
            phrases = details['triggers']['phrases']
            if any(phrase in normalized_text for phrase in phrases):
                function_name = details['function']
                
                # Verifica se a função existe no mapa de ações
                if function_name in self.action_map:
                    print(f"Aurora: Executando a função '{function_name}' para a ação '{action}'")
                    self.action_map[function_name]()  # Executa a função importada
                    return
        print(f"Aurora: {self.get_response('default_response')}")

    def recognize_speech(self):
        while True:
            try:
                recognized_text, audio = self.listen_and_save(prompt="Você: ")
                if recognized_text:
                    if "aurora, por do sol" in recognized_text:
                        print(self.get_response('farewells'))
                        break

                    self.execute_command(recognized_text, audio)

            except srcd.WaitTimeoutError:
                print("Aurora: Continuo ouvindo, tente falar novamente.")
                continue
            except Exception as e:
                print(f"Aurora: Houve um erro inesperado: {e}")
                continue

    def listen_and_save(self, prompt="Diga algo:", lang="pt-BR"):
        with srcd.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print(prompt)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                recognized_text = self.recognizer.recognize_google(audio, language=lang).lower()
                print(f"Texto reconhecido: {recognized_text}")
                return recognized_text, audio
            except srcd.UnknownValueError:
                print("Aurora: Não consegui entender o que você disse.")
                return None, None
            except srcd.RequestError as e:
                print(f"Aurora: Erro no serviço de reconhecimento de voz: {e}")
                return None, None

if __name__ == "__main__":
    aurora = AuroraAI()
    aurora.recognize_speech()