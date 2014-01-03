from datetime import datetime, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Word(models.Model):
    objects = WordManager()

    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.word


class WordManager(models.Manager):
    
    def random(self):
        count = self.count()
        random_index = randint(0, count - 1)
        return self.all()[random_index] 


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
    is_active = models.BooleanField(default=True)

    def deactivate_if_expired(self):
        if self.time_added + timedelta(hours=1) < datetime.utcnow():
            self.is_active = False
            self.save()

    def secs_remaining(self):
        self.deactivate_if_expired()
        if self.is_active:
            return (self.time_added + timedelta(hours=1)) - datetime.utcnow()
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
