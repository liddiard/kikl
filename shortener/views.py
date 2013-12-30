import json
from urlparse import urlparse
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from shortener.models import Cursor, Adjective, Noun, Link

MAX_ANON_LINKS = 10
MAX_AUTH_LINKS = 20


# pages

class FrontPageView(TemplateView):
    
    template_name = "front.html"


def target_view(request):
    pass


class LinkView(DetailView):
    pass


class LinksView(ListView):
    pass


class AboutPageView(TemplateView):
    pass


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

    def get_word(self, word_model, cursor):
        try:
            word = word_model.objects.get(pk=cursor.position)
        except word_model.DoesNotExist:
            word = word_model.objects.get(pk=1)
            cursor.position = 1
        else:
            cursor.position += 1
        cursor.save()
        return word
    
    def post(self, request):
        user_ip = request.META['REMOTE_ADDR']
        target = request.POST.get('target')
        if target is None:
            return self.key_error('Required key "target" not found in request')
        parsed = urlparse(target)
        if not parsed.scheme and parsed.netloc:
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
        adjective_head = Cursor.objects.get(kind='a')
        noun_head = Cursor.objects.get(kind='n')
        adjective = self.get_word(word_model=Adjective, cursor=adjective_head)
        noun = self.get_word(word_model=Noun, cursor=noun_head)
        if request.user.is_authenticated():
            link = Link.objects.get_or_create(adjective=adjective, noun=noun,
                                              target=target, ip_added=user_ip, 
                                              user_added=request.user)[0]
        else:
            link = Link.objects.get_or_create(adjective=adjective, noun=noun,
                                              target=target, 
                                              ip_added=user_ip)[0]
        return self.success(link=link.pk)


class IncreaseDurationView(AuthenticatedAjaxView):
    pass

