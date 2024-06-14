from django.shortcuts import redirect
from django.urls import reverse


class CheckVerifiedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_verified:
            # Redirect to verification page if user is not verified
            if request.path not in [reverse('accounts:send_code'), reverse('accounts:verify_code')]:
                return redirect('accounts:send_code')
        response = self.get_response(request)
        return response
