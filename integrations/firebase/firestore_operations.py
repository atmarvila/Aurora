from connections import FirebaseConnection
from datetime import datetime

class FirestoreOperations:
    def __init__(self, firebase_conn):
        self.db = firebase_conn.get_firestore_client()

    # Adicionar ou atualizar um colaborador
    def upsert_employee(self, employee_data):
        doc_ref = self.db.collection('employees').document(employee_data['document'])
        doc_ref.set(employee_data)
        print(f"Documento adicionado/atualizado com sucesso: {employee_data['name']}")

    # Obter informações de um colaborador pelo documento
    def get_employee(self, document_id):
        doc_ref = self.db.collection('employees').document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"Documento {document_id} não encontrado.")
            return None

    # Atualizar campos específicos de um colaborador
    def update_employee_field(self, document_id, field, value):
        doc_ref = self.db.collection('employees').document(document_id)
        doc_ref.update({field: value})
        print(f"Campo {field} atualizado com sucesso para {value}")

    # Deletar um colaborador pelo documento
    def delete_employee(self, document_id):
        doc_ref = self.db.collection('employees').document(document_id)
        doc_ref.delete()
        print(f"Documento {document_id} deletado com sucesso.")

# Exemplo de uso:
if __name__ == "__main__":
    firebase_conn = FirebaseConnection('/path/to/credentials.json', 'sevent-7197f.appspot.com')
    firestore_ops = FirestoreOperations(firebase_conn)

    # Dados fictícios para teste
    employee_data = {
        'DOB': datetime(2024, 9, 1),
        'city': 'São Paulo',
        'contact_number': '11987654321',
        'district': 'Centro',
        'document': '123456789',
        'document_type': 'CPF',
        'group': 'A',
        'id': 'emp001',
        'last_name': 'Marvila',
        'modication_date': datetime.now(),
        'name': 'Rafael',
        'notification': True,
        'register_date': datetime(2024, 9, 1),
        'role': 'Data Engineer',
        'service_company': 'Tech Solutions',
        'state': 'SP',
        'status': True,
        'supermarket_id': 'sm001'
    }

    # Inserir ou atualizar colaborador
    firestore_ops.upsert_employee(employee_data)

    # Buscar colaborador pelo documento
    collaborator = firestore_ops.get_employee('123456789')
    print(collaborator)

    # Atualizar um campo específico
    firestore_ops.update_employee_field('123456789', 'role', 'Senior Data Engineer')

    # Deletar colaborador
    firestore_ops.delete_employee('123456789')
