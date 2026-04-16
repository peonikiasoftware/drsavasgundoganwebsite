"""Access control for the /doctor-admin/ surface."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def _is_doctor_or_superuser(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.is_staff and user.groups.filter(name="doctor_editors").exists()


def doctor_required(view):
    """Require login + doctor_editors group membership (or superuser)."""
    @wraps(view)
    @login_required(login_url="/doctor-admin/login/")
    def _wrapped(request, *args, **kwargs):
        if not _is_doctor_or_superuser(request.user):
            raise PermissionDenied("You do not have permission to access this page.")
        return view(request, *args, **kwargs)
    return _wrapped
