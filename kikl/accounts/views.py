from django.contrib.sites.models import Site, RequestSite
from registration.backends.default.views import (RegistrationView as 
                                                 BaseRegistrationView)
from registration.models import RegistrationProfile
from registration import signals

from .forms import UserRegistrationForm


class RegistrationView(BaseRegistrationView):

    form_class = UserRegistrationForm
    
    def register(self, request, **cleaned_data):
        email, password = cleaned_data['email'], cleaned_data['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        username = email
            # this is just so the registration profile model won't complain
        new_user = RegistrationProfile.objects.create_inactive_user(username, 
                                                                    email, 
                                                                    password, 
                                                                    site)
        signals.user_registered.send(sender=self.__class__, user=new_user, 
                                     request=request)
        return new_user
