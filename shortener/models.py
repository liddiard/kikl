from django.db import models
from django.contrib.auth.models import User


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
    time_added = models.DateTimeField(auto_now_add=True)
