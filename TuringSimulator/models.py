from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    # also can use instead of default auto_now=True or auto_now_add=True,
    # meaning it will change on every post update/only when its created
    date_posted = models.DateTimeField(default=timezone.now())
    # relation one:many - on_delete specifies what to do if user is deleted,
    # (cascade means delete whole post), but doesnt work
    # both ways - if post is deleted, it wont delete user
    author = models.ForeignKey(User, on_delete=models.CASCADE)

# class InstructionExample(models.Model):
