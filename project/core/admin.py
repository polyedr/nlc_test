from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .constants import ALLOWED_CONTENT_MODELS, APP_LABEL_CORE
from .models import Audio, Page, PageContent, Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for Video model with search by title."""

    list_display = ("id", "title", "counter")
    search_fields = ("title__istartswith",)


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    """Admin configuration for Audio model with search by title."""

    list_display = ("id", "title", "counter")
    search_fields = ("title__istartswith",)


class PageContentInline(admin.TabularInline):
    """Inline block to manage attached content directly on the Page admin page."""

    model = PageContent
    extra = 0
    fields = ("content_type", "object_id", "position")
    ordering = ("position",)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(
                app_label=APP_LABEL_CORE, model__in=ALLOWED_CONTENT_MODELS
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Admin configuration for Page model with search by title and inline content."""

    list_display = ("id", "title")
    search_fields = ("title__istartswith",)
    inlines = [PageContentInline]


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    """Fast control list."""

    list_display = ("id", "page", "content_type", "object_id", "position")
    list_filter = ("page", "content_type")
    search_fields = ("page__title__istartswith",)
    ordering = ("page", "position", "id")
