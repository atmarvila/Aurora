import tempfile
import json
from datetime import datetime
import sys
import os

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.audio_utils import save_audio_wav  # Importa a função utilitária

class AuroraAI:
    def __init__(self):
        pass

    def load_employee_template():
        with open('templates/employees.json', 'r') as file:
            return json.load(file)

    # Função para registrar um colaborador
    def register_collaborator(self, name_audio, name_text):
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
            response, audio = self.listen_and_save()  # Supondo que listen_and_save esteja implementada na classe
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
            save_audio_wav(b''.join(combined_audio_data), final_audio_path)

            # Upload do áudio combinado para o Firebase
            self.upload_to_firebase(final_audio_path, f"Bistek/Employees/{document_number}.wav")

            print(f"Aurora: Cadastro concluído. Áudio salvo como {document_number}.wav")
        else:
            print("Aurora: Não foi possível registrar o colaborador, número de documento não fornecido.")

    def recognize_registered_voice(self, registered_audio_path, new_audio_path):
        # Código para reconhecer voz registrada
        pass

    def execute_command(self, recognized_text):
        command_function_name = nlp_processor(recognized_text)
        if command_function_name:
            command_function = getattr(self, command_function_name, None)
            if command_function:
                command_function()
            else:
                print("Aurora: Desculpe, não consigo executar esse comando.")
        else:
            print("Aurora: Comando não reconhecido. Tente novamente.")

    def recognize_speech(self):
        recognized_text = "cadastro de colaborador"  # Exemplo de texto reconhecido
        self.execute_command(recognized_text)

    def listen_and_save(self):
        # Aqui você implementaria a função listen_and_save usada no register_collaborator
        pass

    def upload_to_firebase(self, local_file, bucket_path):
        # Implementação do upload para o Firebase
        pass