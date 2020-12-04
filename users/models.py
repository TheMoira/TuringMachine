from django.db import models
from django.contrib.auth.models import User


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     firstname = models.CharField(max_length=20, default='unknown')
#     lastname = models.CharField(max_length=20, default='unknown')
#
#     def __str__(self):
#         return f'{self.user.usename} profile'
#
#     def save(self):
#         super().save()