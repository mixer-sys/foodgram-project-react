from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from users.models import Subscription


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',
                  )


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.id is None:
            return False
        return Subscription.objects.filter(
            user_id=obj.id, subscriber=self.context.get('request').user
        ).exists()
