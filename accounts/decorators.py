from functools import wraps
from django.shortcuts import redirect

def firebase_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('firebase_uid'):
            return redirect('signin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view