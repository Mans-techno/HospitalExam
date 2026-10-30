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
]
