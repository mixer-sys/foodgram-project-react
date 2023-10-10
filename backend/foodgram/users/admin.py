from django.contrib import admin
from django.db import models
from django.forms import Textarea

from users.models import User, Subscription


class ViewSettings(admin.ModelAdmin):
    list_per_page = 10
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 45})},
    }


class UserAdmin(ViewSettings):
    list_display = ['id', 'username', 'first_name',
                    'last_name', 'email', 'is_staff', 'is_active',
                    'last_login', 'date_joined', 'role']
    empty_value_display = '-пусто-'
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')


class SubscriptionAdmin(ViewSettings):
    list_display = [field.name for field in Subscription._meta.fields]
    search_fields = ('user__email', 'user__username', 'subscriber__email',
                     'subscriber__username')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
