from django.shortcuts import render, redirect
from django.contrib import messages
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
                import pyrebase
                firebase = pyrebase.initialize_app(settings.FIREBASE_WEB_CONFIG)
                auth_client = firebase.auth()
                user = auth_client.sign_in_with_email_and_password(email, password)
                id_token = user['idToken']
                decoded = firebase_auth.verify_id_token(id_token)
                request.session['firebase_uid'] = decoded['uid']
                messages.success(request, 'Signed in successfully.')
                return redirect('home')
            except Exception:
                messages.error(request, 'Invalid credentials.')
    else:
        form = SignInForm()
    return render(request, 'accounts/signin.html', {'form': form})