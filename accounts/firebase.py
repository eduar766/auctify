import firebase_admin
from firebase_admin import credentials, auth, storage
from django.conf import settings
from pathlib import Path

import firebase_admin.storage

if not firebase_admin._apps:
    # Construir la ruta absoluta al archivo de credenciales
    cred_path = Path(settings.BASE_DIR) / settings.FIREBASE_SERVICE_ACCOUNT
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred, {
        'storageBucket': f"{settings.FIREBASE_PROJECT_ID}.firebasestorage.app"
    })

    print('placebo', firebase_admin.storage.bucket())

# Proveer acceso al bucket en otros módulos
def get_firebase_bucket():
    return firebase_admin.storage.bucket()