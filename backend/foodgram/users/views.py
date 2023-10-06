from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from djoser.views import UserViewSet

from api.serializers import SubscribeSerializer
from users.models import Subscription, User


class APISubscription(APIView, LimitOffsetPagination):
    def get(self, request, user_id=None):
        queryset = User.objects.filter(subscribers__subscriber=request.user)
        results = self.paginate_queryset(queryset, request, view=self)
        serializer = SubscribeSerializer(results, many=True)
        if 'recipes_limit' in request.query_params:
            recipes_limit = int(
                dict(request.query_params).get('recipes_limit')[0]
            )
            serializer = SubscribeSerializer(
                results, many=True, context={"recipes_limit": recipes_limit}
            )
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('user_id'))
        if request.user.id == kwargs.get('user_id'):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(
            user_id=kwargs.get('user_id'), subscriber=request.user
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription, stat = Subscription.objects.get_or_create(
            user_id=kwargs.get('user_id'), subscriber=request.user
        )
        serializer = SubscribeSerializer(user)
        if 'recipes_limit' in request.query_params:
            recipes_limit = int(
                dict(request.query_params).get('recipes_limit')[0]
            )
            serializer = SubscribeSerializer(
                user, context={"recipes_limit": recipes_limit}
            )
        data = serializer.data
        data['is_subscribed'] = True
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscriber = user.subscribers.filter(
            subscriber=request.user)
        if not subscriber.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscriber.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(UserViewSet):
    @action(["get", "put", "patch", "delete"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            if not self.request.user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)
