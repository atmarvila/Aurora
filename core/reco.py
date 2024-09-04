class AuroraAI:
    def __init__(self):
        # Inicializa o reconhecedor de fala
        self.recognizer = srcd.Recognizer()

    def load_employee_template(self):
        with open('templates/employees.json', 'r') as file:
            return json.load(file)

    # Função para registrar um colaborador
    def register_collaborator(self, name_audio, name_text):
        folder_path = tempfile.gettempdir()

        # Carrega o template JSON
        employee_template = self.load_employee_template()

        # Inicializa uma lista para armazenar todos os áudios capturados
        combined_audio_data = []

        # Coleta as informações do colaborador baseado no JSON
        employee_data = {
            "modication_date": datetime.now().isoformat(),
            "register_date": datetime.now().isoformat()
        }

        # Ordem das perguntas e coleta das respostas
        order_of_questions = employee_template['collaborator_registration']['fields']
        document_number = None

        for field, attributes in order_of_questions.items():
            print(f"Aurora: Por favor, informe {attributes['label']}.")
            response, audio = self.listen_and_save()

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