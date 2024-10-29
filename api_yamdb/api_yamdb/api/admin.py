from django.contrib import admin
from .models import Category, Genre, Title, Review, Comments

#Добавляем моделb Category, Genre, Title, Review, Comments в админимстративную панель Django
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comments)
