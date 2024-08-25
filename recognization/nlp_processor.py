from fuzzywuzzy import process, fuzz
from command_map import client_map, employee_map
import spacy

# Carregue o modelo de linguagem para o português
nlp = spacy.load("pt_core_news_sm")

def nlp_processor(recognized_text, map):
    # Use spaCy para processar o texto
    doc = nlp(recognized_text.lower().strip())
    
    # Tokenization: Divida o texto em tokens (palavras)
    tokens = [token.text for token in doc]
    print(f"Tokens: {tokens}")

    # Named Entity Recognition (NER): Identifique entidades no texto
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(f"Entidades reconhecidas: {entities}")

    # Faz o matching do texto reconhecido com o dicionário de comandos
    cleaned_text = " ".join(tokens)  # Recompõe o texto tokenizado para fazer o matching
    matched_command = process.extractOne(cleaned_text, command_map.keys(), scorer=fuzz.partial_ratio)
    
    # Verifica se o match foi suficientemente preciso
    if matched_command and matched_command[1] > 80:  # 80% de similaridade
        return command_map[matched_command[0]]
    else:
        return None

# Bloco de teste
if __name__ == "__main__":
    test_commands = [
        "cadastro de colaborador",
        "Cadastro de Colaboradores",
        "verificar voz registrada",
        "checagem de voz",
        "Registrar colaborador Rafael Marvila"
    ]

    for command in test_commands:
        result = nlp_processor(command)
        print(f"Comando reconhecido: '{command}' -> Função correspondente: '{result}'")