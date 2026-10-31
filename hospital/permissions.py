from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from .models import Doctor


def doctor_required(view_func):
    def has_perm(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not Doctor.objects.filter(user=request.user).exists():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return has_perm


def custom_permission_required(req_permissions):
    def wrapper(view_func):
        def has_perm(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            for perms in req_permissions:
                if request.user.has_perm(perms):
                    return view_func(request, *args, **kwargs)

            raise PermissionDenied
        return has_perm
    return wrapper
