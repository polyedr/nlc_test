from rest_framework import serializers

from .models import Audio, Page, Video


class PageListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for listing pages with minimal fields."""
    url = serializers.HyperlinkedIdentityField(
        view_name="page-detail", lookup_field="pk"
    )

    class Meta:
        model = Page
        fields = ("id", "title", "url")


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for video content objects."""
    type = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ("id", "type", "title", "counter", "video_url", "subtitles_url")

    def get_type(self, obj):
        return "video"


class AudioSerializer(serializers.ModelSerializer):
    """Serializer for audio content objects."""
    type = serializers.SerializerMethodField()

    class Meta:
        model = Audio
        fields = ("id", "type", "title", "counter", "transcript")

    def get_type(self, obj):
        return "audio"


class PageDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed page view with related content."""
    items = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("id", "title", "items")

    def get_items(self, obj: Page):
        items = []
        for pc in obj.contents.select_related("content_type").all():
            c = pc.content
            if isinstance(c, Video):
                items.append(VideoSerializer(c).data)
            elif isinstance(c, Audio):
                items.append(AudioSerializer(c).data)
        return items
