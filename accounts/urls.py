from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('', views.index, name='index'),
    path('authenticate_user/', views.authenticate_user, name='authenticate_user'),
    path('send_verification_email/', views.send_verification_email, name='send_verification_email'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/view/', views.view_profile, name='view_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
