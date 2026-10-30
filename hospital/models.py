from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.


class City(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Hospital(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hospitals')
    name = models.CharField(max_length=70)
    address = models.CharField(max_length=70)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Specialty(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='doctors')
    experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    STATUSES = {'scheduled': 'Запланирована', 'completed': 'Завершена',
                'no_show': 'Неявка', 'cancelled': 'Отменена'}

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    complaint = models.TextField()
    status = models.CharField(max_length=20, choices=STATUSES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['doctor', 'date', 'time']

    def __str__(self):
        return str(self.date)


class emailconfirmationtoken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
