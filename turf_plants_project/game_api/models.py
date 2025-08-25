from django.db import models
from django.contrib.auth.models import User


class Pixel(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    owner = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='pixels')
    description = models.TextField(blank=True, default="")
    planted_on = models.DateTimeField(auto_now_add=True)
    total_xp = models.IntegerField(default=0)


    class Meta:
        unique_together = ('x', 'y')  # avoid duplicates

    def __str__(self):
        return f"({self.x}, {self.y})"


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} (Level {self.level})"