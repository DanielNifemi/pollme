import random

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
                    phone_number = request.POST.get('phone_number')
                    api_url = 'https://www.bulksmsnigeria.com/api/v1/sms/create'
                    api_token = settings.BULK_SMS_API_TOKEN
                    sender = 'YourSenderID'
                    body = f'Your verification code is {verification_code}'

                    payload = {
                        'api_token': api_token,
                        'from': sender,
                        'to': phone_number,
                        'body': body,
                        'dnd': '1'  # Adjust DND option as needed
                    }

                return redirect('accounts:verify_code')
            except Exception as e:
                return render(request, 'accounts/error_sending_code.html')

    else:
        form = UserContactForm()
    return render(request, 'accounts/send_code.html', {'form': form})


@login_required
def verify_code(request):
    if request.method == 'POST':
        user_code = request.POST.get('code')
        stored_code = request.session.get('verification_code')
        email = request.session.get('email')
        phone_number = request.session.get('phone_number')

        if not email and not phone_number:
            messages.error(request, 'Email or phone number is not found in session. Please resend the code.',
                           extra_tags='alert alert-warning alert-dismissible fade show')
            return redirect('accounts:send_code')

        try:
            if user_code == stored_code:
                if email:
                    user = CustomUser.objects.get(email=email)
                else:
                    user = CustomUser.objects.get(phone_number=phone_number)
                user.is_verified = True
                user.save()
                messages.success(request, 'Verification successful.',
                                 extra_tags='alert alert-success alert-dismissible fade show')
                return redirect('home')
            else:
                messages.error(request, 'Invalid verification code.',
                               extra_tags='alert alert-danger alert-dismissible fade show')
                return redirect('accounts:verify_code')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User with this email or phone number does not exist.',
                           extra_tags='alert alert-danger alert-dismissible fade show')
            return redirect('accounts:send_code')

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
