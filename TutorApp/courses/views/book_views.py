from typing import Any, Dict

from courses.forms.book_forms import BookForm
from courses.models import Book
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.mixins import TeacherRequiredMixin


class AddBook(TeacherRequiredMixin, CreateView):
    """
    Simple view that adds book to database via form
    """

    model = Book
    form_class = BookForm
    template_name = "examination_tasks/add_book.html"
    success_url = reverse_lazy("examination_tasks:add_book")

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds the page title to the template context.
        """
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Book")
        return data

    def form_valid(self, form: BookForm) -> HttpResponseRedirect:
        """
        Method for handling the form for adding examinations to the database
        """
        messages.success(self.request, _("Book added successfully!"))
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.role_type != 2:
            return redirect("users:home")
        return super().dispatch(request, *args, **kwargs)
