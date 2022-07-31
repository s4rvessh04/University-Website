from django.http import HttpResponse
from django.shortcuts import redirect


# Restricts user from viewing certain pages while logged in.
# Example: If a user is logged in they are restricted from viewing login page,
# as the user is already logged in.
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('user_view')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


# Restricts users based on the groups.
# The view is allowed to be accessed if user's group is in allowed roles.
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not an Authorised User!!')
        return wrapper_func
    return decorator
