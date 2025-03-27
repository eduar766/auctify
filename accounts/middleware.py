class FirebaseAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uid = request.session.get('firebase_uid')
        if uid:
            request.firebase_uid = uid
        else:
            request.firebase_uid = None
        return self.get_response(request)