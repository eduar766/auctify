from django.shortcuts import render, redirect
from django.contrib import messages
import pyrebase
from accounts.decorators import firebase_login_required
from .forms import SignUpForm, SignInForm
from .firebase import auth
from firebase_admin.auth import EmailAlreadyExistsError
from django.conf import settings
import firebase_admin.auth as firebase_auth



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = auth.create_user(email=email, password=password)
                messages.success(request, 'Account created successfully. Please sign in.')
                return redirect('signin')
            except EmailAlreadyExistsError:
                messages.error(request, 'This email is already registered.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def signin_view(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                print(">>> Iniciando Firebase Web Config...")
                firebase = pyrebase.initialize_app(settings.FIREBASE_WEB_CONFIG)
                auth_client = firebase.auth()

                print(">>> Intentando login con:", email)
                user = auth_client.sign_in_with_email_and_password(email, password)

                print(">>> Login exitoso, verificando token...")
                id_token = user['idToken']
                decoded = firebase_auth.verify_id_token(id_token)

                request.session['firebase_uid'] = decoded['uid']
                messages.success(request, 'Signed in successfully.')
                return redirect('dashboard')

            except Exception as e:
                print(">>> ERROR de Pyrebase:", e)
                messages.error(request, 'Login failed. Please check your credentials.')
    else:
        form = SignInForm()

    return render(request, 'accounts/signin.html', {'form': form})

def signout_view(request):
    request.session.flush()
    messages.success(request, 'Signed out successfully.')
    return redirect('signin')

@firebase_login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')