from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from .services import UserService


class TeacherRequiredMixin(LoginRequiredMixin):
    """
    Mixin, which verifies that the logged-in user has teacher rights.
    """

    def dispatch(self, request, *args, **kwargs):
        user_service = UserService(request.user)

        if not user_service.is_teacher():
            raise PermissionDenied(_("Only teachers can perform this action."))

        return super().dispatch(request, *args, **kwargs)
