from django.db import models


# Create your models here.
class Game(models.Model):
    name = models.CharField()
    description = models.CharField(blank=True, null=True)
    image = models.ImageField(upload_to="media/games/", blank=True, null=True)
    hintForAdmin = models.CharField(blank=True, null=True)
    relateOnId = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        if not self.image and self.relateOnId and self.relateOnId.image:
            self.image = self.relateOnId.image
        super().save(*args,
                   force_insert=force_insert,
                   force_update=force_update,
                   using=using,
                   update_fields=update_fields)

    def __str__(self):
        return self.name
