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
]
