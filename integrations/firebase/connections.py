import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Caminho para o arquivo JSON da conta de serviço
cred = credentials.Certificate('/Users/pels/Downloads/sevent.json')

# Inicialize o Firebase
firebase_admin.initialize_app(cred)

# Obtenha uma referência ao Firestore
db = firestore.client()

# Exemplo: Adicionando um documento à coleção "employees"
doc_ref = db.collection('employees').document('07167041963')
doc_ref.set({
    'DOB': datetime(2024, 9, 1),
    'city': 'São Paulo',
    'contact_number': '11987654321',
    'district': 'Centro',
    'document': '123456789',
    'document_type': 'CPF',
    'group': 'A',
    'id': 'emp001',
    'last_name': 'Marvila',
    'modication_date': datetime(2024, 9, 1),
    'name': 'Rafael',
    'notification': True,
    'register_date': datetime(2024, 9, 1),
    'role': 'Data Engineer',
    'service_company': 'Tech Solutions',
    'state': 'SP',
    'status': True,
    'supermarket_id': 'sm001'
})

print('Documento adicionado com sucesso à coleção employees.')