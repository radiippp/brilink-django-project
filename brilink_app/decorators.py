from django.contrib import messages
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    def decorator(view_function):
        def wrapper(request, *args, **kwargs):
            if request.user.is_staff or request.user.role in allowed_roles:
                return  view_function(request, *args, **kwargs)
            else:
                return redirect('app:login_page')
        return wrapper
    return decorator