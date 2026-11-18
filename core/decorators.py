from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(role):
    """Allow the view only if the user is logged in and user.role matches."""
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                return redirect('dashboard:home')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator