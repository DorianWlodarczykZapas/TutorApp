from django.forms import inlineformset_factory

from ..models import Answer, Question

AnswerFormSet = inlineformset_factory(
    Question, Answer, fields=["text", "is_correct"], extra=4
)
