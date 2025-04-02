from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore
from django.contrib.auth.decorators import login_required
from accounts.decorators import firebase_login_required  # personalizado
import tempfile
from firebase_admin import storage
from accounts.firebase import get_firebase_bucket
from uuid import uuid4
from django.http import Http404

from .forms import AuctionForm, BidForm

db = firestore.client()

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']


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
                ext = image.name.split('.')[-1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    messages.error(request, f"File type .{ext} is not allowed.")
                    return render(request, 'auctions/create.html', {'form': form})
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                for chunk in image.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                filename = f"auctions/{auction_id}/{uuid4()}.{ext}"

                blob = storage.bucket().blob(filename)
                blob.upload_from_filename(temp_file.name)

                blob.make_public()  # 👈 Solo para desarrollo
                uploaded_images.append(blob.public_url)

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
    auctions_ref = db.collection('auctions').order_by('end_time')
    auctions = [doc.to_dict() for doc in auctions_ref.stream()]
    return render(request, 'auctions/list.html', {'auctions': auctions})


def auction_detail_view(request, auction_id):
    doc = db.collection('auctions').document(auction_id).get()
    if not doc.exists:
        messages.error(request, 'Auction not found.')
        return redirect('auction_list')
    auction = doc.to_dict()

    bids = []
    if auction['owner_id'] == request.session.get('firebase_uid'):
        bids_query = db.collection('bids')\
            .where('auction_id', '==', auction_id)\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)
        bids = [b.to_dict() for b in bids_query.stream()]

    return render(request, 'auctions/detail.html', {
        'auction': auction,
        'bids': bids,
        'closed': not auction['active'],
        'winner': auction.get('winner_id'),
        'highest_bid': auction.get('highest_bid', 0),
    })

@firebase_login_required
def auction_edit_view(request, auction_id):
    doc_ref = db.collection('auctions').document(auction_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Http404()

    auction = doc.to_dict()
    if auction['owner_id'] != request.firebase_uid:
        return redirect('auction_detail', auction_id=auction_id)

    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            updated_fields = {
                'title': data['title'],
                'description': data['description'],
                'start_price': data['start_price'],
                'category': data['category'],
                'end_time': data['end_time'],
            }

            # Subida de nuevas imágenes (si las hay)
            files = request.FILES.getlist('images')
            ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
            uploaded_images = []

            if files:
                bucket = get_firebase_bucket()
                for image in files:
                    ext = image.name.split('.')[-1].lower()
                    if ext not in ALLOWED_EXTENSIONS:
                        messages.error(request, f"File type .{ext} is not allowed.")
                        return render(request, 'auctions/edit.html', {'form': form, 'auction_id': auction_id})

                    import tempfile
                    from uuid import uuid4

                    temp_file = tempfile.NamedTemporaryFile(delete=False)
                    for chunk in image.chunks():
                        temp_file.write(chunk)
                    temp_file.flush()

                    filename = f"auctions/{auction_id}/{uuid4()}.{ext}"
                    blob = bucket.blob(filename)
                    blob.upload_from_filename(temp_file.name)
                    blob.make_public()
                    uploaded_images.append(blob.public_url)

                # Si se subieron nuevas imágenes, reemplazar
                if uploaded_images:
                    updated_fields['images'] = uploaded_images

            # Actualizar Firestore con todos los cambios
            doc_ref.update(updated_fields)
            messages.success(request, 'Auction updated.')
            return redirect('auction_detail', auction_id=auction_id)
    else:
        form = AuctionForm(initial=auction)

    return render(request, 'auctions/edit.html', {'form': form, 'auction_id': auction_id})

@firebase_login_required
def auction_delete_view(request, auction_id):
    doc_ref = db.collection('auctions').document(auction_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Http404()
    
    auction = doc.to_dict()
    if auction['owner_id'] != request.firebase_uid:
        return redirect('auction_detail', auction_id=auction_id)

    doc_ref.delete()
    messages.success(request, 'Auction deleted.')
    return redirect('auction_list')

@firebase_login_required
def auction_bid_view(request, auction_id):
    doc_ref = db.collection('auctions').document(auction_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Http404()

    auction = doc.to_dict()
    user_id = request.firebase_uid

    if auction['owner_id'] == user_id:
        messages.error(request, 'You cannot bid on your own auction.')
        return redirect('auction_detail', auction_id=auction_id)

    if not auction.get('active', False):
        messages.error(request, 'This auction is no longer active.')
        return redirect('auction_detail', auction_id=auction_id)

    error_message = None

    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            title = auction.get('title')
            minimum_bid = auction.get('start_price', 0)
            current_highest = auction.get('highest_bid', 0)

            # Verificación visual
            if amount < minimum_bid:
                error_message = f"Your bid is below the starting price (${minimum_bid})."
            elif amount <= current_highest:
                error_message = f"Your bid is not higher than the current highest bid (${current_highest})."

            # Registrar la puja igual
            bid_id = uuid4().hex
            bid_data = {
                'id': bid_id,
                'auction_id': auction_id,
                'user_id': user_id,
                'amount': amount,
                'timestamp': timezone.now(),
                'title': title,
                'url': reverse('auction_detail', kwargs={'auction_id': auction_id}),
            }
            db.collection('bids').document(bid_id).set(bid_data)

            # Solo actualiza highest_bid si es mayor
            if amount > current_highest:
                doc_ref.update({
                    'highest_bid': amount,
                    'winner_id': user_id,
                })

            if error_message:
                # Mostrar advertencia pero no redirigir
                return render(request, 'auctions/bid.html', {
                    'form': form,
                    'auction': auction,
                    'warning': error_message
                })

            messages.success(request, 'Your bid was placed successfully.')
            return redirect('auction_detail', auction_id=auction_id)
    else:
        form = BidForm()

    return render(request, 'auctions/bid.html', {'form': form, 'auction': auction})

@firebase_login_required
def my_bids_view(request):
    print("🔥 ENTRANDO A my_bids_view")
    try:
        user_id = request.firebase_uid
        print("📌 UID:", user_id)

        bids_query = db.collection('bids')\
        .where('user_id', '==', user_id)\
        .order_by('timestamp', direction=firestore.Query.DESCENDING)
        bids = [b.to_dict() for b in bids_query.stream()]
        print("✅ bids:", bids)

        return render(request, 'auctions/my_bids.html', {'bids': bids})

    except Exception as e:
        print("❌ EXCEPCIÓN:", e)
        messages.error(request, 'Error loading bids.')
        return redirect('auction_list')
    
@firebase_login_required
def auction_close_view(request, auction_id):
    doc_ref = db.collection('auctions').document(auction_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Http404()

    auction = doc.to_dict()
    if auction['owner_id'] != request.firebase_uid:
        return redirect('auction_detail', auction_id=auction_id)

    if request.method == 'POST':
        action = request.POST.get('close_type')
        update_fields = {
            'active': False,
            'closed_at': timezone.now()
        }

        if action == 'assign_winner':
            update_fields['sold'] = True
        else:
            update_fields['sold'] = False
            update_fields['winner_id'] = None
            update_fields['highest_bid'] = 0.0

        doc_ref.update(update_fields)
        messages.success(request, 'Auction closed successfully.')
        return redirect('auction_detail', auction_id=auction_id)

    return render(request, 'auctions/close.html', {'auction': auction})