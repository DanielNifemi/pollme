# import random
# import json
# import http.client
#
# import requests
# from django.contrib import messages
# from django.contrib.auth import authenticate, login, logout, get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import render, redirect
# from twilio.rest import Client
#
# from pollme import settings
# # from pollme.settings import TWILIO_PHONE_NUMBER
# from .forms import UserRegistrationForm, ProfileForm, UserContactForm
#
# # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
# CustomUser = get_user_model()
#
#
# def login_user(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             login(request, user)
#             redirect_url = request.GET.get('next', 'home')
#             return redirect(redirect_url)
#         else:
#             messages.error(request, "Full Name Or Phone Number is incorrect!",
#                            extra_tags='alert alert-warning alert-dismissible fade show')
#
#     return render(request, 'accounts/login.html')
#
#
# def logout_user(request):
#     logout(request)
#     return redirect('home')
#
#
# def create_user(request):
#     if request.method == 'POST':
#         check1 = False
#         check2 = False
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             password2 = form.cleaned_data['password2']
#
#             if password != password2:
#                 check1 = True
#                 messages.error(request, 'Passwords did not match!',
#                                extra_tags='alert alert-warning alert-dismissible fade show')
#             if CustomUser.objects.filter(username=username).exists():
#                 check2 = True
#                 messages.error(request, 'Full Name already exists!',
#                                extra_tags='alert alert-warning alert-dismissible fade show')
#
#             if check1 or check2:
#                 messages.error(
#                     request, "Registration Failed!", extra_tags='alert alert-warning alert-dismissible fade show')
#                 return redirect('accounts:register')
#             else:
#                 user = CustomUser.objects.create_user(
#                     username=username, password=password)
#                 messages.success(
#                     request, f'Thanks for registering {user.username}.', extra_tags='alert alert-success '
#                                                                                     'alert-dismissible fade show')
#                 return redirect('accounts:send_code')
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'accounts/register.html', {'form': form})
#
#
# @login_required
# def send_code(request):
#     if request.method == 'POST':
#         form = UserContactForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             phone_number = form.cleaned_data.get('phone_number')
#             contact_method = form.cleaned_data.get('contact_method')
#             verification_code = str(random.randint(1000, 9999))
#
#             try:
#                 request.session['verification_code'] = verification_code
#
#                 if contact_method == 'email':
#                     if not email:
#                         messages.error(request, 'Email is required for email verification.')
#                         return redirect('send_code')
#                     request.session['email'] = email
#                     send_mail(
#                         'Your Verification Code',
#                         f'Your verification code is {verification_code}',
#                         settings.EMAIL_HOST_USER,
#                         [email],
#                         fail_silently=False,
#                     )
#                     messages.success(request, 'Verification code sent to email.')
#                 elif contact_method == 'sms':
#                     if not phone_number:
#                         messages.error(request, 'Phone number is required for SMS verification.')
#                         return redirect('accounts:send_code')
#
#                     # Prepare data for the API
#                     postData = {
#                         'to': phone_number,
#                         'otp': verification_code,
#                         'id': '123',  # Use your actual ID
#                         'domain': 'example.com'  # Use your actual domain
#                     }
#                     content = json.dumps(postData)
#                     headers = {
#                         "Content-type": "application/json"
#                     }
#                     server = 'https://sms.yegara.com/api3/send'
#
#                     # Send request to the API
#                     response = requests.post(server, headers=headers, data=content)
#
#                     # Check response status

#                     if response.status_code != 200:
#                         messages.error(request, 'Failed to send SMS. Please try again.')
#                         return redirect('send_code')
#
#                     messages.success(request, 'Verification code sent to phone.')
#
#                 return redirect('accounts:verify_code')
#             except Exception as e:
#                 return render(request, 'accounts/error_sending_code.html', {'error': str(e)})
#
#     else:
#         form = UserContactForm()
#     return render(request, 'accounts/send_code.html', {'form': form})
#
#
# @login_required
# def verify_code(request):
#     if request.method == 'POST':
#         user_code = request.POST.get('code')
#         stored_code = request.session.get('verification_code')
#
#         if user_code == stored_code:
#             request.user.is_verified = True
#             request.user.save()
#             messages.success(request, 'Verification successful. Your phone number is verified.')
#             return redirect('home')
#         else:
#             messages.error(request, 'Invalid verification code. Please try again.')
#             return redirect('accounts:verify_code')
#
#     return render(request, 'accounts/verify_code.html')

import json
import logging
import os
import secrets
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

import requests
from allauth.account.utils import send_email_confirmation
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.forms import ProfileForm
from accounts.models import CustomUser

logger = logging.getLogger(__name__)


def index(request):
    response = render(request, 'accounts/index.html')
    response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
    return response


def authenticate_user(request):
    user_json_url = request.GET.get('user_json_url')
    if not user_json_url:
        return JsonResponse({'error': 'user_json_url parameter is missing'}, status=400)

    try:
        # Use requests for secure communication
        response = urlopen(user_json_url)
        data = json.loads(response.read().decode())
    except (URLError, HTTPError) as e:
        logger.error(f"Failed to fetch user data: {e}")
        return JsonResponse({'error': 'Failed to fetch user data', 'details': str(e)}, status=500)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        logger.error(f"Response content: {response.read().decode()}")
        return JsonResponse({'error': 'Failed to decode JSON response', 'details': str(e)}, status=500)

    user_country_code = data.get("user_country_code")
    user_phone_number = data.get("user_phone_number")
    user_email = data.get("user_email")

    if user_phone_number:
        try:
            user, created = CustomUser.objects.get_or_create(
                phone_number=user_phone_number,
                defaults={'country_code': user_country_code, 'email': user_email}
            )
        except IntegrityError as e:
            logger.error(f"IntegrityError: {e}")
            if 'phone_number' in str(e):
                return JsonResponse({'error': 'User with this phone number already exists'}, status=400)
            else:
                return JsonResponse({'error': 'An error occurred during user creation'}, status=500)

        # Assuming verification is successful
        user.is_verified = True
        user.save()

    elif user_email:
        # Redirect to email sign-in flow
        return redirect('accounts:send_verification_email')
    else:
        return JsonResponse({'error': 'User data is missing phone number and email'}, status=400)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'success': True, 'redirect_url': redirect('polls:list').url})


def perform_phone_email_verification(user_info):
    """
    Performs phone email verification using phone.email's functionalities.

    Args:
        user_info (dict): Dictionary containing user information (country code, phone number, email).

    Returns:
        bool: True if verification is successful, False otherwise.
    """
    verification_url = "https://phone.email/api/verify"
    data = {
        "phone_number": user_info["user_phone_number"],
        "email": user_info["user_email"],
        "country_code": user_info.get("user_country_code"),
    }
    response = requests.post(verification_url, json=data)

    if response.status_code == 200:
        verification_data = response.json()
        is_verified = verification_data.get("verified", False)
        return is_verified
    else:
        logger.error(f"Verification failed with status code: {response.status_code}")
        return False


def generate_verification_code():
    return secrets.token_urlsafe(16)


def send_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        verification_code = generate_verification_code()
        user = CustomUser.objects.create_user(email=email)
        user.verification_code = verification_code
        user.save()
        current_site = get_current_site(request)
        send_email_confirmation(request, user, verification_code, current_site)
        return render(request, 'accounts/verification_sent.html')
    return render(request, 'accounts/send_verification_email.html')


def verify_email(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        try:
            user = CustomUser.objects.get(email=request.user.email)
            if user.verification_code == verification_code:
                user.is_verified = True
                user.save()
                login(request, user)
                return redirect('polls:list')
            else:
                return render(request, 'accounts/verification_failed.html', {'error': 'Invalid verification code'})
        except CustomUser.DoesNotExist:
            return render(request, 'accounts/verification_failed.html', {'error': 'User not found'})
    return render(request, 'accounts/verification_form.html')


def login_view(request):
    return redirect('accounts:index')


def logout_user(request):
    logout(request)
    return redirect('home')


@login_required
def view_profile(request):
    return render(request, 'accounts/view_profile.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:view_profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/update_profile.html', {'form': form})
