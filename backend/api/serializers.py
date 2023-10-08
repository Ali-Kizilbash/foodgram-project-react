from django.conf import settings
from django.db.transaction import atomic
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscribe, User


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscribe.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        )


class RecipeSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscribe.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSimpleSerializer(
            recipes, many=True, read_only=True)
        return serializer.data


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = '__all__'

    def validate_author(self, author):
        VALIDATION_ERROR = 'Невозможно подписаться на самого себя'
        if self.context['request'].user == author:
            raise serializers.ValidationError(VALIDATION_ERROR)
        return author

    def to_representation(self, instance):
        return SubscriptionsSerializer(
            instance.author,
            context=self.context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = Favorite
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном'
            ),
        )

    def to_representation(self, instance):
        return RecipeSimpleSerializer(
            instance.recipe,
            context=self.context
        ).data


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = Cart
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в корзине'
            ),
        )

    def to_representation(self, instance):
        return RecipeSimpleSerializer(
            instance.recipe,
            context=self.context
        ).data


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        read_only=True,
        many=True,
        source='recipes'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Cart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, amount):
        VALIDATION_ERROR = (
            'Допустимые значения количества ингредиента: '
            f'{settings.INGREDIENT_AMOUNT_MIN} - '
            f'{settings.INGREDIENT_AMOUNT_MAX}'
        )
        if not (settings.INGREDIENT_AMOUNT_MAX >= amount
                >= settings.INGREDIENT_AMOUNT_MIN):
            raise serializers.ValidationError(VALIDATION_ERROR)
        return amount


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    cooking_time = serializers.IntegerField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date', 'author')

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=i['id'].id),
                amount=i['amount']
            ) for i in ingredients
        ])

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.ingredients.clear()
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def validate(self, data):
        NO_INGREDIENT_ERROR = 'В рецепте не могут отсутствовать ингредиенты'
        NO_TAG_ERROR = 'В рецепте не могут отсутствовать теги'
        INGREDIENT_DUPLICATE_ERROR = 'Ингредиенты не могут дублироваться'
        TAG_DUPLICATE_ERROR = 'Теги не могут дублироваться'
        COOKING_TIME_ERROR = (
            'Допустимые значения времени приготовления: '
            f'{settings.COOKING_TIME_MIN} - '
            f'{settings.COOKING_TIME_MAX}'
        )
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(NO_INGREDIENT_ERROR)
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(NO_TAG_ERROR)
        validated_ingredients = []
        for ingredient in ingredients:
            if ingredient not in validated_ingredients:
                validated_ingredients.append(ingredient)
            else:
                raise serializers.ValidationError(INGREDIENT_DUPLICATE_ERROR)
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(TAG_DUPLICATE_ERROR)
        if not (settings.COOKING_TIME_MAX >=
                data.get('cooking_time')
                >= settings.COOKING_TIME_MIN):
            raise serializers.ValidationError(COOKING_TIME_ERROR)
        return data

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context=self.context
        ).data
