from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'post_count',
        'is_staff',
        'is_active'
    )
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'bio')}),
    )

    @display(description='Количество постов')
    def post_count(self, obj):
        return obj.posts.count()

    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'role',
                    'post_count',
                    'is_staff',
                    'is_active')


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.unregister(Group)
