from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from store.form import SignUpForm
from django.contrib.messages import get_messages



def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    storage = get_messages(request)
    storage.used = True

    if not request.user.is_authenticated and request.method == "GET":
        messages.info(request, "Please sign in to continue.")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
