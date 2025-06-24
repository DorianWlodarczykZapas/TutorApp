import factory

from .models import Answer, Quiz


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    type = 1  # Real numbers
    question = factory.Faker("sentence")
    explanation = factory.Faker("paragraph")
    question_picture = None
    explanation_picture = None


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Answer

    quiz = factory.SubFactory(QuizFactory)
    text = factory.Faker("word")
    is_correct = False
