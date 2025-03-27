import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from pathlib import Path

if not firebase_admin._apps:
    # Construir la ruta absoluta al archivo de credenciales
    cred_path = Path(settings.BASE_DIR) / settings.FIREBASE_SERVICE_ACCOUNT
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)