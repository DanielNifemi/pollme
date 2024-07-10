from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, MyUserToken


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'is_verified')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MyUserToken)
