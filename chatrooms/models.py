from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
# Create your models here.


class Topic(models.Model):
    name = models.CharField(max_length=200, db_index=True)

    def __str__(self) -> str:
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)

    topic = models.ForeignKey(
        Topic, on_delete=models.PROTECT, related_name="rooms")
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="rooms")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Message(models.Model):
    content = models.TextField(max_length=1000, validators=[
                               MinLengthValidator(2)])

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='messages')
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE, related_name='messages')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.content[:50]
