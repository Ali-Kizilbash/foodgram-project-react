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
        'following',
        'recipes'
    )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', )
