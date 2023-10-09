from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageNumberLimitPaginator
from api.permissions import IsAuthAndIsAuthorOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeListSerializer, SubscribeSerializer,
                             SubscriptionsSerializer, TagSerializer)
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscribe, User


class UserViewSet(DjoserViewSet):
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AllowAny,)
    http_method_names = ('get', 'post', 'delete')
    pagination_class = PageNumberLimitPaginator

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={
                    'user': request.user.id,
                    'author': author.id
                },
                context={
                    'request': request
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscribe.objects.filter(
            user=request.user,
            author=author
        )

        if not subscription:
            return Response(
                {'errors': 'Нет подписки на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get', ),
            permission_classes=[IsAuthAndIsAuthorOrReadOnly])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = PageNumberLimitPaginator
    permission_classes = (IsAuthAndIsAuthorOrReadOnly, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    def serializer_create(self, user_id, pk, serializer):
        serializer = serializer(
            data={
                'user': user_id,
                'recipe': pk
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def serializer_delete(self, user_id, pk, model):
        recipe = model.objects.filter(
            user=user_id,
            recipe=pk
        )
        if not recipe:
            return Response(
                {'errors': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated, ))
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.serializer_create(
                request.user.id,
                kwargs.get('pk'),
                FavoriteSerializer
            )
        return self.serializer_delete(
            request.user.id,
            kwargs.get('pk'),
            Favorite
        )

    @action(detail=False, methods=('get', ),
            permission_classes=(IsAuthAndIsAuthorOrReadOnly, ))
    def download_shopping_cart(self, request):
        items = RecipeIngredient.objects.select_related(
            'recipe', 'ingredient'
        ).filter(recipe__shopping_carts__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total=Sum('amount')
        )
        items_list = []
        for item in items:
            items_list.append(
                f"{item['ingredient__name']} - "
                f"{item['total']} {item['ingredient__measurement_unit']}"
            )
        RESPONSE_CONTENT_TYPE = 'text/plan'
        response = HttpResponse(
            '\n'.join(items_list),
            content_type=RESPONSE_CONTENT_TYPE
        )
        response['Content-Disposition'] = \
            f'attachment; filename={settings.SHOP_LIST_FILE_NAME}'
        return response

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthAndIsAuthorOrReadOnly, ))
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            return self.serializer_create(
                request.user.id,
                kwargs.get('pk'),
                CartSerializer
            )
        return self.serializer_delete(
            request.user.id,
            kwargs.get('pk'),
            Cart
        )


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
