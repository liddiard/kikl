from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class Adjective(models.Model):
    word = models.CharField(max_length=16)


class Noun(models.Model):
    word = models.CharField(max_length=16)


class Link(models.Model):
    adjective = models.ForeignKey('Adjective')
    noun = models.ForeignKey('Noun')
    target = models.URLField() 
        # default max_length=200; may need to be increased
    ip_added = models.IPAddressField()
    user_added = models.ForeignKey(User, blank=True, null=True)
    time_added = models.DateTimeField(default=datetime.utcnow())

    def is_active(self):
        return self.time_added + datetime.timedelta(hours=1) > datetime.utcnow()

    def secs_remaining(self):
        if self.is_active(): 
            return (self.time_added + datetime.timedelta(hours=1)) - \
                    datetime.utcnow()
        else:
            return 0
