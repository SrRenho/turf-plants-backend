from django.db import models
from django.contrib.auth.models import User


class Pixel(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        unique_together = ('x', 'y')  # avoid duplicates

    def __str__(self):
        return f"({self.x}, {self.y})"


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, blank=True)