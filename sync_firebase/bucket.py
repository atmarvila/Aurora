import firebase_admin
from firebase_admin import credentials, storage

# Caminho para o arquivo JSON da conta de serviço
cred = credentials.Certificate('/Users/pels/Downloads/sevent.json')

# Inicialize o Firebase
firebase_admin.initialize_app(cred, {
    'storageBucket': 'sevent-7197f.appspot.com'
})

# Obtenha uma referência ao bucket de armazenamento
bucket = storage.bucket()

# Caminho do arquivo local que você deseja fazer upload
local_file = '/caminho/para/arquivo.txt'
blob = bucket.blob('pasta_no_bucket/arquivo.txt')

# Faça o upload do arquivo
blob.upload_from_filename(local_file)

print('Upload do arquivo concluído com sucesso.')