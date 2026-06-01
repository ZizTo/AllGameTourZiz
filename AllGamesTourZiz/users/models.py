from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to="media/avatars/", blank=True, null=True)
    MMR = models.PositiveIntegerField(default=1000, db_index=True)
    WinKol = models.PositiveIntegerField(default=0)
    LoseKol = models.PositiveIntegerField(default=0)
    games = models.ManyToManyField("games.Game", through="GameStats")

class GameStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE)
    MMR = models.PositiveIntegerField(default=1000, db_index=True)
    WinKol = models.PositiveIntegerField(default=0)
    LoseKol = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.game.name}"


