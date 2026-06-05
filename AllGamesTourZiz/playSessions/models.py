from django.db import models
import secrets
import string

def generate_code():
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(12))

class PlaySession(models.Model):
    uniqueCode = models.CharField(max_length=12, default=generate_code, unique=True, editable=False)
    players = models.ManyToManyField("users.User", through="SessionParticipants")
    game = models.ForeignKey("games.Game", on_delete=models.SET_NULL, blank=True, null=True)
    status = models.PositiveSmallIntegerField(null=False, blank=False, default=0)
    # 0. Не начато
    # 1. Игра идёт
    # 2. Отменён
    # 3. Ничья
    # 4. Первый победил
    # 5. Второй победил
    # 6. Тд...

    def __str__(self):
        return f"{self.game.name} | {self.uniqueCode}"


class SessionParticipants(models.Model):
    session = models.ForeignKey(PlaySession, on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    numberInSession = models.PositiveIntegerField(default=0)  # Two or more in one is Team
    points = models.PositiveIntegerField(null=True, blank=True)  # use somthing
    time = models.DurationField(null=True, blank=True)           # from this two
    mmrChange = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} | {self.session.uniqueCode}"
