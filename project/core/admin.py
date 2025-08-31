from django.contrib import admin

from .models import Audio, Page, PageContent, Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "counter")
    search_fields = ("title__istartswith",)


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "counter")
    search_fields = ("title__istartswith",)


class PageContentInline(admin.TabularInline):
    model = PageContent
    extra = 0
    fields = ("content_type", "object_id", "position")
    ordering = ("position",)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title__istartswith",)
    inlines = [PageContentInline]


# Fast control list
@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("id", "page", "content_type", "object_id", "position")
    list_filter = ("page", "content_type")
    search_fields = ("page__title__istartswith",)
    ordering = ("page", "position", "id")
