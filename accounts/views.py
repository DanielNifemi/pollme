import requests  # You'll need to install the requests library
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import CustomUserCreationForm, ProfileCompletionForm, PhoneLoginForm
from .models import CustomUser


def register(request):
    if request.method == 'POST':
        if 'phone' in request.POST:
            return handle_phone_auth(request)
        else:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('home')
    else:
        form = CustomUserCreationForm()
    phone_form = PhoneLoginForm()
    return render(request, 'accounts/register.html', {'form': form, 'phone_form': phone_form})


def user_login(request):
    if request.method == 'POST':
        if 'phone' in request.POST:
            return handle_phone_auth(request)
        else:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    phone_form = PhoneLoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'phone_form': phone_form})


def handle_phone_auth(request):
    phone = request.POST.get('phone')
    if phone:
        # Send OTP using phone.email service
        response = requests.post('https://phone.email/send', data={
            'phone': phone,
            'api_key': 'oxELv6LvCjcBlSAdMUcPm4IKNsXrkhAc'
        })
        if response.status_code == 200:
            # Store phone number in session for verification
            request.session['phone_login'] = phone
            return redirect('accounts:verify_otp')
    # If phone is not provided or API call failed, redirect back with error
    return redirect(request.path)


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        phone = request.session.get('phone_login')
        if phone and otp:
            # Verify OTP using phone.email service
            response = requests.post('https://phone.email/verify', data={
                'phone': phone,
                'code': otp,
                'api_key': 'oxELv6LvCjcBlSAdMUcPm4IKNsXrkhAc'
            })
            if response.status_code == 200:
                # OTP verified, log in or create user
                user, created = CustomUser.objects.get_or_create(phone=phone)
                login(request, user)
                del request.session['phone_login']
                return redirect('home')
    return render(request, 'accounts/verify_otp.html')


@login_required
def profile_completion(request):
    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileCompletionForm(instance=request.user)
    return render(request, 'accounts/profile_completion.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileCompletionForm(instance=request.user)
    return render(request, 'accounts/update_profile.html', {'form': form})


@login_required
def user_search(request):
    query = request.GET.get('q')
    users = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
    ) if query else CustomUser.objects.none()
    return render(request, 'accounts/user_search.html', {'users': users, 'query': query})
