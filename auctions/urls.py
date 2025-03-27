from django.urls import path
from .views import auction_create_view, auction_list_view, auction_detail_view

urlpatterns = [
    path('', auction_list_view, name='auction_list'),
    path('create/', auction_create_view, name='auction_create'),
    path('<str:auction_id>/', auction_detail_view, name='auction_detail'),
]