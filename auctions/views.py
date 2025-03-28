from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore
from django.contrib.auth.decorators import login_required
from accounts.decorators import firebase_login_required  # personalizado
import tempfile
from firebase_admin import storage
from accounts.firebase import get_firebase_bucket
from uuid import uuid4

from .forms import AuctionForm

db = firestore.client()


@firebase_login_required
def auction_create_view(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            auction_id = firestore.client().collection('auctions').document().id

            # 🔼 Subida de imágenes a Storage
            uploaded_images = []
            files = request.FILES.getlist('images')
            for image in files:
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                for chunk in image.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                ext = image.name.split('.')[-1]
                filename = f"auctions/{auction_id}/{uuid4()}.{ext}"

                blob = storage.bucket().blob(filename)
                blob.upload_from_filename(temp_file.name)

                blob.make_public()  # 👈 Solo para desarrollo
                uploaded_images.append(blob.public_url)

            print('peorrrrrrrrr', uploaded_images)
            auction_data = {
                'id': auction_id,
                'owner_id': request.firebase_uid,
                'title': data['title'],
                'description': data['description'],
                'images': uploaded_images,
                'start_price': float(data['start_price']),
                'category': data.get('category') or '',
                'start_time': timezone.now(),
                'end_time': data['end_time'],
                'active': True,
                'highest_bid': 0.0,
                'winner_id': None,
                'payment_status': "pending",
                'closed_at': None,
                'sold': False,
                'cancelled_by_owner': False,
            }

            db.collection('auctions').document(auction_id).set(auction_data)
            messages.success(request, 'Auction created successfully.')
            return redirect('auction_list')
    else:
        form = AuctionForm()

    return render(request, 'auctions/create.html', {'form': form})


def auction_list_view(request):
    auctions_ref = db.collection('auctions').where('active', '==', True).order_by('end_time')
    auctions = [doc.to_dict() for doc in auctions_ref.stream()]
    return render(request, 'auctions/list.html', {'auctions': auctions})


def auction_detail_view(request, auction_id):
    doc = db.collection('auctions').document(auction_id).get()
    if not doc.exists:
        messages.error(request, 'Auction not found.')
        return redirect('auction_list')
    auction = doc.to_dict()
    return render(request, 'auctions/detail.html', {'auction': auction})