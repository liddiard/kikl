from random import randint
from datetime import datetime, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class WordManager(models.Manager):
    
    def random(self):
        count = self.count()
        random_index = randint(0, count - 1)
        return self.all()[random_index] 


class Word(models.Model):
    objects = WordManager()

    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.word


class Adjective(Word):
    word = models.CharField(max_length=16)


class Noun(Word):
    word = models.CharField(max_length=16)


class Link(models.Model):
    adjective = models.ForeignKey('Adjective')
    noun = models.ForeignKey('Noun')
    target = models.URLField() 
        # default max_length=200; may need to be increased
    ip_added = models.IPAddressField()
    duration = models.PositiveIntegerField(default=60) # minutes
    user_added = models.ForeignKey(User, blank=True, null=True)
    time_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def path(self):
        return "%s-%s" % (self.adjective, self.noun)

    def deactivate_if_expired(self):
        if self.time_added + timedelta(hours=1) < datetime.now():
            self.is_active = False
            self.save()

    def secs_remaining(self):
        time_delta = (self.time_added + timedelta(minutes=self.duration))\
                      - datetime.now()
        delta_secs = time_delta.total_seconds()
        print delta_secs
        if delta_secs > 0:
            return delta_secs
        else:
            return 0

    def clean(self):
        try:
            link = Link.objects.filter(is_active=True)\
                               .get(adjective=self.adjective, noun=self.noun)
        except Link.DoesNotExist:
            pass
        else:
            if link.pk != self.pk:
                raise ValidationError('An active link with the chosen '
                                      'adjective and noun already exists.')

    def __unicode__(self):
        return u"%s-%s \u00bb %s" % (self.adjective, self.noun, self.target)
