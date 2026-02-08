from django.forms import inlineformset_factory
from videos.models import Video, VideoTimestamp

VideoTimestampFormSet = inlineformset_factory(
    Video,
    VideoTimestamp,
    fields=["label", "start_time", "timestamp_type"],
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
