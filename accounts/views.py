from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileCompletionForm
from .models import CustomUser


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


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
