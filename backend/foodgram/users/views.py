from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from users.models import Subscription, User
from api.serializers import SubscribeSerializer


class APISubscription(APIView):

    def get(self, request, user_id=None):
        users = User.objects.filter(subscribers__subscriber=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(users, request)
        serializer = SubscribeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('user_id'))
        subscriber = user.subscribers.filter(
            subscriber=request.user)
        if not subscriber.exists():
            Subscription(
                user_id=kwargs.get('user_id'), subscriber=request.user
                ).save()
        serializer = SubscribeSerializer(user)
        data = serializer.data
        data['is_subscribed'] = subscriber.exists()
        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('user_id'))
        subscriber = user.subscribers.filter(
            subscriber=request.user)
        if subscriber.exists():
            subscriber.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
