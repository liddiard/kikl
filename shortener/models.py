import uuid
from random import randint
from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core import serializers


class WordManager(models.Manager):
    
    def random(self):
        count = self.count()
        random_index = randint(0, count - 1)
        return self.all()[random_index] 


class Word(models.Model):
    objects = WordManager()

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.word


class Adjective(Word):
    word = models.CharField(max_length=16, unique=True, db_index=True)


class Noun(Word):
    word = models.CharField(max_length=16, unique=True, db_index=True)


class Link(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    adjective = models.ForeignKey('Adjective', on_delete=models.CASCADE)
    noun = models.ForeignKey('Noun', on_delete=models.CASCADE)
    # match max length of Django's URLValidator
    target = models.URLField(max_length=2048)
    ip_added = models.GenericIPAddressField(db_index=True)
    # how long the link will be active in hours
    duration = models.DurationField(default=timedelta(hours=24))
    time_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def path(self):
        return f"{self.adjective}-{self.noun}"

    def update_is_active(self):
        is_active = self.time_added + self.duration > timezone.now()
        if self.is_active != is_active:
            self.save()

    def secs_remaining(self):
        time_delta = (self.time_added + timedelta(hours=self.duration))\
                      - timezone.now()
        delta_secs = time_delta.total_seconds()
        if delta_secs > 0:
            return int(round(delta_secs))
        else:
            return 0

    def clean(self):
        try:
            link = Link.objects.filter(is_active=True)\
                               .get(adjective=self.adjective, noun=self.noun)
        except Link.DoesNotExist:
            pass
        else:
            if link.uuid != self.uuid:
                raise ValidationError('An active link with the chosen '
                                      'adjective and noun already exists.')
    
    def to_json(self):
        return {
            'uuid': self.uuid,
            'path': self.path(),
            'target': self.target,
            'duration': int(self.duration.total_seconds() / 3600), # hours
            'time_added': self.time_added,
            'is_active': self.is_active
        }

    def __str__(self):
        return f"{self.adjective}-{self.noun} » {self.target}"
