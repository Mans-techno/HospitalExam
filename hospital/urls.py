from django.urls import path
from .views import *


urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('confirm/<uuid:token>/', confirm_email_view, name='confirm_email'),
    path('specialties/', specialty_list_view, name='specialty_list'),
    path('specialties/<int:pk>/', hospital_list_view, name='hospital_list'),
    path('specialties/<int:pk>/hospitals/<int:hospital_pk>/', doctor_list_view, name='doctor_list'),
    path('appointments/', appointment_list_view, name='appointment_list'),
    path('doctors/<int:pk>/book/', appointment_create_view, name='appointment_create'),
    path('appointments/<int:pk>/update/', appointment_update_view, name='appointment_update'),
    path('appointments/<int:pk>/delete/', appointment_delete_view, name='appointment_delete'),
    path('doctor/', doctor_appointments_view, name='doctor_appointments'),
    path('doctor/<int:pk>/status/', doctor_status_view, name='doctor_status'),

    path('manage/cities/', manage_city_list_view, name='manage_city_list'),
    path('manage/cities/create/', manage_city_create_view, name='manage_city_create'),
    path('manage/cities/<int:pk>/update/', manage_city_update_view, name='manage_city_update'),
    path('manage/cities/<int:pk>/delete/', manage_city_delete_view, name='manage_city_delete'),
    path('manage/specialties/', manage_specialty_list_view, name='manage_specialty_list'),
    path('manage/specialties/create/', manage_specialty_create_view, name='manage_specialty_create'),
    path('manage/specialties/<int:pk>/update/', manage_specialty_update_view, name='manage_specialty_update'),
    path('manage/specialties/<int:pk>/delete/', manage_specialty_delete_view, name='manage_specialty_delete'),
    path('manage/hospitals/', manage_hospital_list_view, name='manage_hospital_list'),
    path('manage/hospitals/create/', manage_hospital_create_view, name='manage_hospital_create'),
    path('manage/hospitals/<int:pk>/update/', manage_hospital_update_view, name='manage_hospital_update'),
    path('manage/hospitals/<int:pk>/delete/', manage_hospital_delete_view, name='manage_hospital_delete'),
    path('manage/doctors/', manage_doctor_list_view, name='manage_doctor_list'),
    path('manage/doctors/create/', manage_doctor_create_view, name='manage_doctor_create'),
    path('manage/doctors/<int:pk>/update/', manage_doctor_update_view, name='manage_doctor_update'),
    path('manage/doctors/<int:pk>/delete/', manage_doctor_delete_view, name='manage_doctor_delete'),
]
