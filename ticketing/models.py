from django.db import models
import uuid
import bcrypt

# Create your models here.

class Device(models.Model):
    id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=200, null=True)

    def _str_(self):
        return self.name

    def encrypt(self,password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, bcrypt.gensalt())

    def compare(self,password):
        password = password.encode('UTF-8')
        try:
            return bcrypt.checkpw(password, self.password.encode("utf-8"))
        except:
            return False

#Cars in parking with slot in corresponding level
class Car(models.Model):
    deviceId = models.ForeignKey(Device, on_delete=models.CASCADE, null=False, default="")
    regno = models.CharField(max_length=15, default=uuid.uuid1, primary_key=True)
    color = models.CharField(max_length=10, default='nocolor')
    status = models.CharField(max_length=3, default='in')
    slot = models.IntegerField(default=100)
    level = models.IntegerField(default=100)
    createdAt = models.DateTimeField(auto_now_add=True, blank=True, null = True)
    def __str__(self):
        return self.regno


class Ticket(models.Model):
    carId = models.ForeignKey(Car, on_delete=models.CASCADE,  null=False)
    slotAllotted = models.CharField(max_length=3, default=00)
    ticketNo = models.CharField(primary_key=True, max_length=3, default=uuid.uuid1)
    def __str__(self):
        return self.ticketNo

