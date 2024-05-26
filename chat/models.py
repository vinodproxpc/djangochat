from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    from_who = models.ForeignKey(User, on_delete=models.PROTECT, default=None, related_name="from_who")
    to_who = models.ForeignKey(User, on_delete=models.PROTECT, default=None, related_name="to_who")
    message = models.TextField()
    date = models.DateField(null=True)
    time = models.TimeField()
    has_been_seen = models.BooleanField(default=False)



class UserChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=None)
    channel_name = models.CharField(max_length=100)


