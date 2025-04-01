from django.urls import path
from .views import auction_create_view, auction_list_view, auction_detail_view, auction_delete_view, auction_edit_view

urlpatterns = [
    path('', auction_list_view, name='auction_list'),
    path('create/', auction_create_view, name='auction_create'),
    path('<str:auction_id>/', auction_detail_view, name='auction_detail'),
    path('<str:auction_id>/edit/', auction_edit_view, name='auction_edit'),
    path('<str:auction_id>/delete/', auction_delete_view, name='auction_delete'),
]