import json
from urlparse import urlparse

from django.http import HttpResponse, Http404
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import login as django_login, logout as django_logout
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView

from .models import Adjective, Noun, Link
from .forms import ConfirmCurrentUserForm

MAX_ANON_LINKS = 10
MAX_AUTH_LINKS = 20
MAX_LINK_DURATION = 120

# utility functions

def get_link(adjective, noun):
    a = get_object_or_404(Adjective, word=adjective)
    n = get_object_or_404(Noun, word=noun)
    link = get_object_or_404(Link, is_active=True, adjective=a, noun=n)
    return link

# pages

class FrontPageView(TemplateView):
    
    template_name = "front.html"

    def get_context_data(self, **kwargs):
        context = super(FrontPageView, self).get_context_data(**kwargs)
        context['sample_paths'] = ['goofy-lemur', 'fabulous-anteater', 
                                   'awkward-puffin']
        return context


def target_view(request, adjective, noun):
    link = get_link(adjective, noun)
    link.deactivate_if_expired()
    if link.is_active:
        return redirect(link.target)
    else:
        raise Http404


class LinkView(TemplateView):
    
    template_name = "link.html"

    def get_context_data(self, **kwargs):
        context = super(LinkView, self).get_context_data(**kwargs)
        adjective = self.kwargs.get('adjective')
        noun = self.kwargs.get('noun')
        context['link'] = get_link(adjective, noun)
        context['MAX_LINK_DURATION'] = MAX_LINK_DURATION
        return context


class LinksView(TemplateView):
    
    template_name = "links.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LinksView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LinksView, self).get_context_data(**kwargs)
        context['links'] = Link.objects.filter(is_active=True, 
                                               user_added=self.request.user)
        context['MAX_LINK_DURATION'] = MAX_LINK_DURATION
        return context


class AboutPageView(TemplateView):
    pass


class AccountDeleteView(FormView):

    template_name = "registration/account_delete_form.html" 
    form_class = ConfirmCurrentUserForm
    success_url = reverse_lazy('account_delete_complete')

    def get_form_kwargs(self):
        kwargs = super(AccountDeleteView, self).get_form_kwargs()
        kwargs.update({
            'request' : self.request
        })
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('front')
        return super(AccountDeleteView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        user.is_active = False
        user.save()
        django_logout(self.request)
        return redirect('account_delete_complete')


class AccountDeleteCompleteView(TemplateView):
    
    template_name = "registration/account_delete_complete.html"


# api

class AjaxView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            return super(AjaxView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404

    def json_response(self, **kwargs):
        return HttpResponse(json.dumps(kwargs), content_type="application/json")

    def success(self, **kwargs):
        return self.json_response(result=0, **kwargs)

    def error(self, error_type, message):
        return self.json_response(result=1, error=error_type, message=message)

    def authentication_error(self):
        return self.error("AuthenticationError", "User is not authenticated.")

    def access_error(self, message):
        return self.error("AccessError", message)

    def key_error(self, message):
        return self.error("KeyError", message)

    def does_not_exist(self, message):
        return self.error("DoesNotExist", message)

    def validation_error(self, message):
        return self.error("ValidationError", message)


class AuthenticatedAjaxView(AjaxView):
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(AuthenticatedAjaxView, self).dispatch(request, *args,
                                                               **kwargs)
        else:
            return self.authentication_error()


class AddLinkView(AjaxView):

    def post(self, request):
        user_ip = request.META['REMOTE_ADDR']
        target = request.POST.get('target')
        if target is None:
            return self.key_error('Required key "target" not found in request.')
        parsed = urlparse(target)
        if not parsed.scheme and not parsed.netloc:
            return self.validation_error('Target URL is missing protocol or '
                                         'domain.')
        if request.user.is_authenticated():
            max_links = MAX_AUTH_LINKS
            links = Link.objects.filter(user_added=request.user)
        else:
            max_links = MAX_ANON_LINKS
            links = Link.objects.filter(ip_added=user_ip)
        active_links = links.filter(is_active=True)
        if (active_links.count() >= max_links):
            return self.access_error('User already has max number of active '
                                     'links (%s).' % max_links)
        adjective = Adjective.objects.order_by('?')[0]
        noun_query = '''
            SELECT * FROM shortener_noun WHERE shortener_noun.id NOT IN 
            (SELECT shortener_noun.id FROM shortener_noun LEFT OUTER JOIN 
            shortener_link ON shortener_link.noun_id = shortener_noun.id 
            WHERE shortener_link.is_active = 't' AND 
            shortener_link.adjective_id = %s) ORDER BY RANDOM() LIMIT 1;
        '''
        noun_queryset = Noun.objects.raw(noun_query, [adjective.id])
        try:
            noun = noun_queryset[0]
        except IndexError:
            return self.error(error_type='CapacityError', message='No '
                              'combination of link words is available at this '
                              'time.')
        if request.user.is_authenticated():
            link = Link.objects.get_or_create(adjective=adjective, noun=noun,
                                              target=target, ip_added=user_ip, 
                                              user_added=request.user)[0]
        else:
            link = Link.objects.get_or_create(adjective=adjective, noun=noun,
                                              target=target, 
                                              ip_added=user_ip)[0]
        return self.success(link=link.pk, path=link.path())


class IncreaseDurationView(AuthenticatedAjaxView):
    
    def post(self, request):
        link = request.POST.get('link')
        if link is None:
            return self.key_error('Required key "link" not found in request.')
        try:
            l = Link.objects.get(id=int(link))
        except (ValueError, Link.DoesNotExist):
            return self.does_not_exist('Link matching id %s does not exist.' 
                                       % link)
        l.deactivate_if_expired()
        if not l.is_active:
            return self.does_not_exist('Link matching id %s has expired.'
                                       % link)
        if l.duration >= MAX_LINK_DURATION:
            return self.access_error('Max link duration of %s minutes reached.' 
                                     % MAX_LINK_DURATION)
        l.duration += 10
        l.save()
        return self.success(link=l.pk, new_duration=l.duration, 
                            new_secs_remaining=l.secs_remaining())
