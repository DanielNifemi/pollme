from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.authtoken.models import Token


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=14, blank=True, null=True)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    is_verified = models.BooleanField(
        default=False,
        help_text='Designates whether the user is verified.',
        verbose_name='verification status'
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class MyUserToken(Token):
    # Add any additional fields you want to display in the admin

    class Meta:
        verbose_name = "My User Token"
        verbose_name_plural = "My User Tokens"
