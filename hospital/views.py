from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import *
from .helpers import *
# Create your views here.


def home_view(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not email:
            return render(request, 'register.html', context={'error': "Введите email"})
        if not password1 or password1 != password2:
            return render(request, 'register.html', context={'error': "Пароли не совпадают"})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', context={'error': "Такой пользователь уже есть"})

        user = User.objects.create_user(username=email, email=email, password=password2, is_active=False)
        token = emailconfirmationtoken.objects.create(user=user)
        send_confirmation_email(token)
        return HttpResponse("Проверьте почту")

    return render(request, 'register.html')


def confirm_email_view(request, token):
    token = get_object_or_404(emailconfirmationtoken, token=token)
    token.user.is_active = True
    token.user.save()
    token.delete()
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is None:
            return render(request, 'login.html', context={'error': "Неверный логин или пароль"})

        login(request, user)
        return redirect('home')

    return render(request, 'login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

    return render(request, 'logout.html')


def specialty_list_view(request):
    specialties = Specialty.objects.all()
    return render(request, 'specialty_list.html', context={'specialties': specialties})


def hospital_list_view(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    hospitals = Hospital.objects.filter(doctors__specialty=specialty).distinct()
    return render(request, 'hospital_list.html', context={'specialty': specialty, 'hospitals': hospitals})
