import pyrebase
import environ

env = environ.Env()
environ.Env.read_env()

firebase_config = {
    "apiKey": env("FIREBASE_API_KEY"),
    "authDomain": env("FIREBASE_AUTH_DOMAIN"),
    "projectId": env("FIREBASE_PROJECT_ID"),
    "storageBucket": env("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": env("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": env("FIREBASE_APP_ID"),
    "databaseURL": env("FIREBASE_DATABASE"),
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

email = input("Email: ")
password = input("Password: ")

try:
    user = auth.sign_in_with_email_and_password(email, password)
    print("✅ Login successful")
    print("ID Token:", user['idToken'][:50], '...')
except Exception as e:
    print("❌ Error logging in:", e)