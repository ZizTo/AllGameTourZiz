from django.db import models


# Create your models here.
class Game(models.Model):
    name = models.CharField()
    description = models.CharField(blank=True, null=True)
    image = models.ImageField(upload_to="media/games/", blank=True, null=True)
    hintForAdmin = models.CharField(blank=True, null=True)
    relateOnId = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name
