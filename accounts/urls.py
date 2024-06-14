from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('register/', views.create_user, name='register'),
    path('send-code/', views.send_code, name='send_code'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
]
