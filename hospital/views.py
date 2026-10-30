from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from django.utils.http import url_has_allowed_host_and_scheme
from .models import *
from .helpers import *
from .permissions import *
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

        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
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


def doctor_list_view(request, pk, hospital_pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    hospital = get_object_or_404(Hospital, pk=hospital_pk)
    doctors = Doctor.objects.filter(specialty=specialty, hospital=hospital)
    return render(request, 'doctor_list.html', context={'specialty': specialty, 'hospital': hospital, 'doctors': doctors})



def get_form_data(request, doctor, pk=None):
    date = parse_date(request.POST.get('date', ''))
    time = parse_time(request.POST.get('time', ''))
    complaint = request.POST.get('complaint', '').strip()

    if date is None or time is None or not complaint:
        return date, time, complaint, "Заполните все поля"
    if date < timezone.localdate():
        return date, time, complaint, "Эта дата уже прошла"
    if Appointment.objects.filter(doctor=doctor, date=date, time=time).exclude(pk=pk).exists():
        return date, time, complaint, "Это время уже занято"

    return date, time, complaint, None


@login_required
def appointment_list_view(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointment_list.html', context={'appointments': appointments})


@login_required
def appointment_create_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    context = {'doctor': doctor}
    if request.method == 'POST':
        date, time, complaint, error = get_form_data(request, doctor)
        if error:
            return render(request, 'appointment_form.html', context={**context, 'error': error})

        Appointment.objects.create(patient=request.user, doctor=doctor, date=date, time=time, complaint=complaint)
        return redirect('appointment_list')

    return render(request, 'appointment_form.html', context=context)


@login_required
def appointment_update_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
    context = {'appointment': appointment, 'doctor': appointment.doctor}
    if request.method == 'POST':
        date, time, complaint, error = get_form_data(request, appointment.doctor, appointment.pk)
        if error:
            return render(request, 'appointment_form.html', context={**context, 'error': error})

        appointment.date = date
        appointment.time = time
        appointment.complaint = complaint
        appointment.save()
        return redirect('appointment_list')

    return render(request, 'appointment_form.html', context=context)


@login_required
def appointment_delete_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')

    return render(request, 'appointment_delete.html', context={'appointment': appointment})


@doctor_required
def doctor_appointments_view(request):
    appointments = Appointment.objects.filter(doctor=request.user.doctor).order_by('date', 'time')
    return render(request, 'doctor_appointments.html', context={'appointments': appointments})


@doctor_required
def doctor_status_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user.doctor)
    if request.method == 'POST':
        status = request.POST.get('status', '')
        if status in ['completed', 'no_show']:
            appointment.status = status
            appointment.save()

    return redirect('doctor_appointments')
