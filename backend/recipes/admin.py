from django.contrib import admin

from recipes.models import (Favorite, RecipeIngredient,
                            Ingredient, Recipe,
                            Tag, Cart)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('^name', )


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('ingredient__measurement_unit', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('^name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)
    list_display = (
        'id',
        'name',
        'author',
        'text',
        'image',
        'favorite_count',
        'tag',
        'cooking_time'
    )
    list_filter = ('tags', )
    search_fields = ('author__username', 'name')

    @admin.display(description='Теги')
    def tag(self, recipe):
        tags = []
        for tag in recipe.tags.all():
            tags.append(tag.name)
        return ' ::: '.join(tags)

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', )
    list_filter = ('recipe__tags__name', )
    search_fields = ('user__username', 'recipe__name')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('recipe__tags', )
    search_fields = ('user__username', 'recipe__name')
