from django.shortcuts import redirect
from django.urls import reverse

# class AgeVerificationMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Exclude the age verification URL and other specific URLs to prevent infinite redirect loop
#         excluded_paths = [reverse('age_verification'), reverse('delete_image')]
#         if request.path not in excluded_paths:
#             # Check if the user has verified their age
#             if not request.session.get('age_verified', False):
#                 logger.info(f"User has not verified age. Redirecting to age verification page from {request.path}")
#                 # If not verified, redirect to the age verification page
#                 return redirect('age_verification')
        
#         # If verified, proceed with the request
#         response = self.get_response(request)
#         return response
