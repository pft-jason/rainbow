from django.shortcuts import redirect
from django.urls import reverse

class AgeVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude the age verification URL to prevent infinite redirect loop
        if request.path != reverse('age_verification'):
            # Check if the user has verified their age
            if not request.session.get('age_verified', False):
                # If not verified, redirect to the age verification page
                return redirect('age_verification')
        
        # If verified, proceed with the request
        response = self.get_response(request)
        return response
