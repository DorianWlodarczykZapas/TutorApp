import factory

from .models import Video


class VideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Video

    title = factory.Faker("sentence", nb_words=4)
    youtube_url = factory.Faker("url")
    type = 1
    subcategory = "Algebra"
    level = "1"
