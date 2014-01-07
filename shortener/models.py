from random import randint
from datetime import datetime, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, 
                                        BaseUserManager)


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, 
                     **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        email = self.normalize_email(email)
        if not email:
            raise ValueError('The given username must be set')
        user = self.model(email=email, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    is_staff = models.BooleanField('staff status', default=False,
        help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name


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
    user_added = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, 
                                   null=True)
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
            if link.pk != self.pk:
                raise ValidationError('An active link with the chosen '
                                      'adjective and noun already exists.')

    def __unicode__(self):
        return u"%s-%s \u00bb %s" % (self.adjective, self.noun, self.target)
