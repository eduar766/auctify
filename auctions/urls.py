from django.urls import path
from .views import auction_bid_view, auction_create_view, auction_list_view, auction_detail_view, auction_delete_view, auction_edit_view, my_bids_view

urlpatterns = [
    path('', auction_list_view, name='auction_list'),
    path('create/', auction_create_view, name='auction_create'),
    path('my-bids/', my_bids_view, name='my_bids'),
    path('<str:auction_id>/', auction_detail_view, name='auction_detail'),
    path('<str:auction_id>/edit/', auction_edit_view, name='auction_edit'),
    path('<str:auction_id>/delete/', auction_delete_view, name='auction_delete'),
    path('<str:auction_id>/bid/', auction_bid_view, name='auction_bid'),
]