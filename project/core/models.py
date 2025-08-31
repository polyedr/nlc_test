from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Page(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.title


class ContentBase(models.Model):
    title = models.CharField(max_length=255)
    counter = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Video(ContentBase):
    video_url = models.URLField()
    subtitles_url = models.URLField(blank=True)


class Audio(ContentBase):
    transcript = models.TextField()


class PageContent(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="contents")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey("content_type", "object_id")
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("position", "id")
