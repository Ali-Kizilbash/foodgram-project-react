from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email', )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', )
    search_fields = ('user', 'author', )
