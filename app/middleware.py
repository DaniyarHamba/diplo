from django.shortcuts import redirect
from django.urls import reverse


class RedirectToSignupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_urls = [
            reverse('registration'),
            reverse('login'),
            reverse('change_password'),
        ]

        if not request.user.is_authenticated and not any(request.path.startswith(url) for url in allowed_urls) and not request.path.startswith('/admin/'):
            return redirect('login')

        response = self.get_response(request)
        return response
