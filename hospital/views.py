from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
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
        user = User.objects.filter(email=email).first()
        if user:
            user = authenticate(request, username=user.username, password=password)
        if not user:
            return render(request, 'login.html', context={'error': "Неверный логин или пароль"})

        login(request, user)

        next_url = request.GET.get('next')
        if next_url:
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



@custom_permission_required(['hospital.view_city'])
def manage_city_list_view(request):
    cities = City.objects.all()
    return render(request, 'manage/city_list.html', context={'cities': cities})


@custom_permission_required(['hospital.add_city'])
def manage_city_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'manage/city_form.html', context={'error': "Введите название"})

        City.objects.create(name=name)
        return redirect('manage_city_list')

    return render(request, 'manage/city_form.html')


@custom_permission_required(['hospital.change_city'])
def manage_city_update_view(request, pk):
    city = get_object_or_404(City, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'manage/city_form.html', context={'city': city, 'error': "Введите название"})

        city.name = name
        city.save()
        return redirect('manage_city_list')

    return render(request, 'manage/city_form.html', context={'city': city})


@custom_permission_required(['hospital.delete_city'])
def manage_city_delete_view(request, pk):
    city = get_object_or_404(City, pk=pk)
    if request.method == 'POST':
        city.delete()
        return redirect('manage_city_list')

    return render(request, 'manage/delete.html', context={'item': city, 'back': 'manage_city_list'})



@custom_permission_required(['hospital.view_specialty'])
def manage_specialty_list_view(request):
    specialties = Specialty.objects.all()
    return render(request, 'manage/specialty_list.html', context={'specialties': specialties})


@custom_permission_required(['hospital.add_specialty'])
def manage_specialty_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'manage/specialty_form.html', context={'error': "Введите название"})

        Specialty.objects.create(name=name)
        return redirect('manage_specialty_list')

    return render(request, 'manage/specialty_form.html')


@custom_permission_required(['hospital.change_specialty'])
def manage_specialty_update_view(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'manage/specialty_form.html', context={'specialty': specialty, 'error': "Введите название"})

        specialty.name = name
        specialty.save()
        return redirect('manage_specialty_list')

    return render(request, 'manage/specialty_form.html', context={'specialty': specialty})


@custom_permission_required(['hospital.delete_specialty'])
def manage_specialty_delete_view(request, pk):
    specialty = get_object_or_404(Specialty, pk=pk)
    if request.method == 'POST':
        specialty.delete()
        return redirect('manage_specialty_list')

    return render(request, 'manage/delete.html', context={'item': specialty, 'back': 'manage_specialty_list'})



def get_hospital_data(request):
    name = request.POST.get('name', '').strip()
    address = request.POST.get('address', '').strip()
    phone = request.POST.get('phone', '').strip()
    city_id = request.POST.get('city', '')
    city = City.objects.filter(pk=city_id).first() if city_id.isdigit() else None

    if not name or not address or not phone or city is None:
        return name, address, phone, city, "Заполните все поля"

    return name, address, phone, city, None


@custom_permission_required(['hospital.view_hospital'])
def manage_hospital_list_view(request):
    hospitals = Hospital.objects.all()
    return render(request, 'manage/hospital_list.html', context={'hospitals': hospitals})


@custom_permission_required(['hospital.add_hospital'])
def manage_hospital_create_view(request):
    cities = City.objects.all()
    if request.method == 'POST':
        name, address, phone, city, error = get_hospital_data(request)
        if error:
            return render(request, 'manage/hospital_form.html', context={'cities': cities, 'error': error})

        Hospital.objects.create(name=name, address=address, phone=phone, city=city)
        return redirect('manage_hospital_list')

    return render(request, 'manage/hospital_form.html', context={'cities': cities})


@custom_permission_required(['hospital.change_hospital'])
def manage_hospital_update_view(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    cities = City.objects.all()
    if request.method == 'POST':
        name, address, phone, city, error = get_hospital_data(request)
        if error:
            return render(request, 'manage/hospital_form.html', context={'hospital': hospital, 'cities': cities, 'error': error})

        hospital.name = name
        hospital.address = address
        hospital.phone = phone
        hospital.city = city
        hospital.save()
        return redirect('manage_hospital_list')

    return render(request, 'manage/hospital_form.html', context={'hospital': hospital, 'cities': cities})


@custom_permission_required(['hospital.delete_hospital'])
def manage_hospital_delete_view(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        hospital.delete()
        return redirect('manage_hospital_list')

    return render(request, 'manage/delete.html', context={'item': hospital, 'back': 'manage_hospital_list'})



def get_doctor_data(request):
    hospital_id = request.POST.get('hospital', '')
    specialty_id = request.POST.get('specialty', '')
    experience = request.POST.get('experience', '')
    hospital = Hospital.objects.filter(pk=hospital_id).first() if hospital_id.isdigit() else None
    specialty = Specialty.objects.filter(pk=specialty_id).first() if specialty_id.isdigit() else None

    if hospital is None or specialty is None:
        return hospital, specialty, experience, "Выберите больницу и специальность"
    if not experience.isdigit():
        return hospital, specialty, experience, "Введите стаж"

    return hospital, specialty, experience, None


@custom_permission_required(['hospital.view_doctor'])
def manage_doctor_list_view(request):
    doctors = Doctor.objects.all()
    return render(request, 'manage/doctor_list.html', context={'doctors': doctors})


@custom_permission_required(['hospital.add_doctor'])
def manage_doctor_create_view(request):
    context = {
        'users': User.objects.filter(doctor__isnull=True),
        'hospitals': Hospital.objects.all(),
        'specialties': Specialty.objects.all(),
    }
    if request.method == 'POST':
        user_id = request.POST.get('user', '')
        user = context['users'].filter(pk=user_id).first() if user_id.isdigit() else None
        hospital, specialty, experience, error = get_doctor_data(request)
        if user is None:
            error = "Выберите пользователя"
        if error:
            return render(request, 'manage/doctor_form.html', context={**context, 'error': error})

        Doctor.objects.create(user=user, hospital=hospital, specialty=specialty, experience=experience)
        return redirect('manage_doctor_list')

    return render(request, 'manage/doctor_form.html', context=context)


@custom_permission_required(['hospital.change_doctor'])
def manage_doctor_update_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    context = {'doctor': doctor, 'hospitals': Hospital.objects.all(), 'specialties': Specialty.objects.all()}
    if request.method == 'POST':
        hospital, specialty, experience, error = get_doctor_data(request)
        if error:
            return render(request, 'manage/doctor_form.html', context={**context, 'error': error})

        doctor.hospital = hospital
        doctor.specialty = specialty
        doctor.experience = experience
        doctor.save()
        return redirect('manage_doctor_list')

    return render(request, 'manage/doctor_form.html', context=context)


@custom_permission_required(['hospital.delete_doctor'])
def manage_doctor_delete_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        return redirect('manage_doctor_list')

    return render(request, 'manage/delete.html', context={'item': doctor, 'back': 'manage_doctor_list'})
