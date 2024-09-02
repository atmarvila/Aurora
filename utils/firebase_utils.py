import firebase_admin
from firebase_admin import credentials, storage

def initialize_firebase(cred_path, bucket_name):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': bucket_name
    })

def upload_to_firebase(local_file, bucket_path):
    bucket = storage.bucket()
    blob = bucket.blob(bucket_path)
    blob.upload_from_filename(local_file)
    print(f"Upload do arquivo {local_file} para {bucket_path} concluído com sucesso.")