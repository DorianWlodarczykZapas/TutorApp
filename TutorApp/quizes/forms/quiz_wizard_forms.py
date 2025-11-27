from django import forms


class QuizStepForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # answers = question.answers.all()
