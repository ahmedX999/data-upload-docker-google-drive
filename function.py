import os
import json
import boto3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64

def decrypt_env_var(encrypted_value):
    kms_client = boto3.client('kms')
    decrypted_value = kms_client.decrypt(
        CiphertextBlob=base64.b64decode(encrypted_value)
    )['Plaintext'].decode('utf-8')
    return decrypted_value

def create_drive_service(client_id, client_secret, refresh_token):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret
    )
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

def lambda_handler(event, context):
    # Récupérer les informations de connexion depuis les variables d'environnement chiffrées
    encrypted_client_id = os.environ['ENCRYPTED_CLIENT_ID']
    encrypted_client_secret = os.environ['ENCRYPTED_CLIENT_SECRET']
    encrypted_refresh_token = os.environ['ENCRYPTED_REFRESH_TOKEN']
    
    try:
        client_id = decrypt_env_var(encrypted_client_id)
        client_secret = decrypt_env_var(encrypted_client_secret)
        refresh_token = decrypt_env_var(encrypted_refresh_token)

        drive_service = create_drive_service(client_id, client_secret, refresh_token)
        
        # Récupérer la liste des fichiers du Google Drive
        results = drive_service.files().list(pageSize=10).execute()
        items = results.get('files', [])
        
        response = {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
    return response
