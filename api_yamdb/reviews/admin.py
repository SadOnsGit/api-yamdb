from django.contrib import admin
from reviews.models import Category, Comment, Genre, Review, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "category", "name", "year", "description")
    list_display_links = ("name", "description")
    list_editable = ("category",)
    list_filter = ("genre", "category")
    empty_value_display = "-пусто-"
    search_fields = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    list_editable = ("slug",)
    list_display_links = ("pk",)
    empty_value_display = "-пусто-"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    list_editable = ("slug",)
    list_display_links = ("pk",)
    empty_value_display = "-пусто-"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "author", "score", "pub_date")
    list_filter = ("score", "pub_date")
    search_fields = ("text", "author__username", "title__name")
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "review", "author", "pub_date")
    list_filter = ("pub_date",)
    search_fields = ("text", "author__username", "review__title__name")
    empty_value_display = "-пусто-"
