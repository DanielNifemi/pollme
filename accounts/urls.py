from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/complete/', views.profile_completion, name='profile_completion'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('search/', views.user_search, name='user_search'),
]