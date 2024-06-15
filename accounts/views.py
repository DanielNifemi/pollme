import random
import json
import http.client

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from twilio.rest import Client

from pollme import settings
# from pollme.settings import TWILIO_PHONE_NUMBER
from .forms import UserRegistrationForm, ProfileForm, UserContactForm

# client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
CustomUser = get_user_model()



def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'home')
            return redirect(redirect_url)
        else:
            messages.error(request, "Full Name Or Phone Number is incorrect!",
                           extra_tags='alert alert-warning alert-dismissible fade show')

    return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect('home')


def create_user(request):
    if request.method == 'POST':
        check1 = False
        check2 = False
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']

            if password != password2:
                check1 = True
                messages.error(request, 'Passwords did not match!',
                               extra_tags='alert alert-warning alert-dismissible fade show')
            if CustomUser.objects.filter(username=username).exists():
                check2 = True
                messages.error(request, 'Full Name already exists!',
                               extra_tags='alert alert-warning alert-dismissible fade show')

            if check1 or check2:
                messages.error(
                    request, "Registration Failed!", extra_tags='alert alert-warning alert-dismissible fade show')
                return redirect('accounts:register')
            else:
                user = CustomUser.objects.create_user(
                    username=username, password=password)
                messages.success(
                    request, f'Thanks for registering {user.username}.', extra_tags='alert alert-success '
                                                                                    'alert-dismissible fade show')
                return redirect('accounts:send_code')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def send_code(request):
    if request.method == 'POST':
        form = UserContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            contact_method = form.cleaned_data.get('contact_method')
            verification_code = str(random.randint(100000, 999999))

            try:
                request.session['verification_code'] = verification_code

                if contact_method == 'email':
                    if not email:
                        return JsonResponse({'message': 'Email is required for email verification'}, status=400)
                    request.session['email'] = email
                    send_mail(
                        'Your Verification Code',
                        f'Your verification code is {verification_code}',
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )
                elif contact_method == 'sms':
                    if not phone_number:
                        return JsonResponse({'message': 'Phone number is required for SMS verification'}, status=400)
                    request.session['phone_number'] = phone_number
                    conn = http.client.HTTPSConnection("textflow-sms-api.p.rapidapi.com")
                    payload = json.dumps({
                        "to": phone_number,
                        "message": f"Your verification code is {verification_code}",
                        "sender": "YourSenderID"
                    })

                    headers = {
                        'x-rapidapi-key': "d42f68d9bfmsh597540a8266a3dep1140f1jsnc32c7ba76702",
                        'x-rapidapi-host': "textflow-sms-api.p.rapidapi.com",
                        'Content-Type': "application/json"
                    }

                    conn.request("POST", "/service/check", payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    response_data = json.loads(data.decode("utf-8"))

                    if response_data.get('status') != 'success':
                        return JsonResponse({'message': response_data.get('message', 'An error occurred')}, status=400)

                return redirect('accounts:verify_code')
            except Exception as e:
                return render(request, 'accounts/error_sending_code.html', {'error': str(e)})

    else:
        form = UserContactForm()
    return render(request, 'accounts/send_code.html', {'form': form})


@login_required
def verify_code(request):
    if request.method == 'POST':
        user_code = request.POST.get('code')
        stored_code = request.session.get('verification_code')

        if user_code == stored_code:
            request.user.is_verified = True
            request.user.save()
            messages.success(request, 'Verification successful. Your phone number is verified.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
            return redirect('verify_code')

    return render(request, 'accounts/verify_code.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
