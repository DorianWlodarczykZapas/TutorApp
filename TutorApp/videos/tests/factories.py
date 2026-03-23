from datetime import timedelta

import factory
from courses.tests.factories import SectionFactory
from videos.models import Video, VideoTimestamp


class VideoFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Video

    title = factory.Sequence(lambda n: f"Video {n}")
    youtube_url = factory.Sequence(lambda n: f"https://youtu.be/video{n:011d}")
    section = factory.SubFactory(SectionFactory)
    subject = 1
    level = 2


class VideoTimestampFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VideoTimestamp

    video = factory.SubFactory(VideoFactory)
    label = factory.Sequence(lambda n: f"Timestamp {n}")
    start_time = factory.Sequence(lambda n: timedelta(minutes=n))
    timestamp_type = VideoTimestamp.TimestampType.EXERCISE
