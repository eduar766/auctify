from django.urls import path
from .views import signup_view, signin_view, dashboard_view, signout_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('signin/', signin_view, name='signin'),
    path('signout/', signout_view, name='signout'),
    path('dashboard/', dashboard_view, name='dashboard'),
]