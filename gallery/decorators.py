# dirtydeedz/gallery/decorators.py
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def age_verification_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('age_verified', False):
            return redirect('age_verification')
        return view_func(request, *args, **kwargs)
    return _wrapped_view