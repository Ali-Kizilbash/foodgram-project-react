from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from colorfield.fields import ColorField

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Ингредиент',
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=settings.MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения',
        help_text='Единица измерения'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_measurement'
            ),
        )

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=settings.TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Тег',
        help_text='Название тега'
    )
    slug = models.SlugField(
        max_length=settings.TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name='slug',
        help_text='Слаг'
    )
    color = ColorField(
        max_length=settings.TAG_COLOR_MAX_LENGTH,
        default='#FF0000',
        unique=True,
        verbose_name='Цвет',
        help_text='Цвет'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=settings.RECIPE_NAME_MAX_LENGTH,
        verbose_name='Рецепт',
        help_text='Название рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Имя автора'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Теги'
    )
    image = models.ImageField(
        upload_to='media',
        verbose_name='Изображение',
        help_text='Изображение'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления',
        default=settings.COOKING_TIME_MIN,
        validators=(
            MinValueValidator(
                settings.COOKING_TIME_MIN,
                f'Минимальное значение - {settings.COOKING_TIME_MIN}'
            ),
            MaxValueValidator(
                settings.COOKING_TIME_MAX,
                f'Максимальное значение - {settings.COOKING_TIME_MAX}'
            )
        )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        help_text='Ингредиенты',
        related_name='recipe',
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}, {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Добавлено в избранное',
        help_text='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Любимый рецепт',
        help_text='Рецепт',
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} ::: {self.recipe}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент',
        help_text='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Количество ингредиента',
        default=settings.INGREDIENT_AMOUNT_MIN,
        validators=(
            MinValueValidator(
                settings.INGREDIENT_AMOUNT_MIN,
                f'Минимальное значение - {settings.INGREDIENT_AMOUNT_MIN}'
            ),
            MaxValueValidator(
                settings.INGREDIENT_AMOUNT_MAX,
                f'Максимальное значение - {settings.INGREDIENT_AMOUNT_MAX}'
            )
        )
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт',
        help_text='Рецепт',
    )

    def __str__(self):
        return f'{self.recipe} ::: {self.ingredient} ::: {self.amount}'


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Добавлено в корзину',
        related_name='shopping_carts',
        help_text='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
        related_name='shopping_carts',
        help_text='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} ::: {self.recipe}'
