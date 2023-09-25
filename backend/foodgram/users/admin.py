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
    list_display = [field.name for field in User._meta.fields]
    empty_value_display = '-пусто-'
    list_filter = ['username', 'email']


class SubscriptionAdmin(ViewSettings):
    list_display = [field.name for field in Subscription._meta.fields]
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
