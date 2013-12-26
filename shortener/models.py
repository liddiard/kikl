from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User


class Cursor(models.Model):
    position = models.PositiveIntegerField(default=1)
    KIND_CHOICES = (('a', 'Adjective'), ('n', 'Noun'))
    kind = models.CharField(max_length=1, choices=KIND_CHOICES)

    def __unicode__(self):
        return "%s: %s" % (self.kind, self.position)


class Word(models.Model):

    class Meta:
        abstract = True
    
    def random(self):
        count = self.count()
        random_index = randint(0, count - 1)
        return self.all()[random_index] 

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
    user_added = models.ForeignKey(User, blank=True, null=True)
    time_added = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return self.time_added + timedelta(hours=1) > datetime.utcnow()

    def secs_remaining(self):
        if self.is_active(): 
            return (self.time_added + timedelta(hours=1)) - datetime.utcnow()
        else:
            return 0

    def __unicode__(self):
        return u"%s-%s \u00bb %s" % (self.adjective, self.noun, self.target)
