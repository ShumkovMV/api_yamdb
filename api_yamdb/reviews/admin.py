from django.contrib import admin

from .models import Category, Genre, Title, Review, Comments

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'genre')
    search_fields = ('name',)
    list_filter = ('genre',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'author')
    search_fields = ('title__name',)
    list_filter = ('author',)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'text', 'author')
    search_fields = ('review__title__name',)
    list_filter = ('author',)