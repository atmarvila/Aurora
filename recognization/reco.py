
from nlp_processor import nlp_processor

class AuroraAI:
    def __init__(self):
        # Inicializa componentes necessários
        pass

    def register_collaborator(self, name_audio, name_text):
        # Código para cadastrar colaborador
        pass
        
    def register_employee(self, name_audio, name_text):
        # Código para cadastrar colaborador
        pass

    def recognize_registered_voice(self, registered_audio_path, new_audio_path):
        # Código para reconhecer voz registrada
        pass

    def execute_command(self, recognized_text):
        command_function_name = nlp_processor(recognized_text)
        if command_function_name:
            command_function = getattr(self, command_function_name, None)
            if command_function:
                # Chama a função correspondente
                command_function()
            else:
                print("Aurora: Desculpe, não consigo executar esse comando.")
        else:
            print("Aurora: Comando não reconhecido. Tente novamente.")

    def recognize_speech(self):
        recognized_text = "cadastro de colaborador"  # Exemplo de texto reconhecido
        self.execute_command(recognized_text)

# Instancia a classe e inicia o processo
aurora = AuroraAI()
aurora.recognize_speech()