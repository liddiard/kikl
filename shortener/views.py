import json
from urlparse import urlparse
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from shortener.models import Adjective, Noun, Link

MAX_ANON_LINKS = 10
MAX_AUTH_LINKS = 200

# pages

class FrontPageView(TemplateView):
    
    template_name = "front.html"


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
    
    def post(self, request):
        user_ip = request.META['REMOTE_ADDR']
        target = request.POST.get('target')
        if target is None:
            return self.key_error('Required key "target" not found in request')
        parsed = urlparse(target)
        if not parsed.scheme and parsed.netloc:
            return self.validation_error("Target URL is missing protocol or "
                                         "domain.")
        if user.is_authenticated():
            max_links = MAX_AUTH_LINKS
            active_links = [x for x in Link.objects\
                            .filter(user=request.user) 
                            if x.is_active()]
        else:
            max_links = MAX_ANON_LINKS
            active_links = [x for x in Link.objects\
                            .filter(ip_added=user_ip) 
                            if x.is_active()]
        if (len(active_links) >= max_links):
            return self.access_error('User already has max number of active '
                                     'links (%s).' % max_links)
        if user.is_authenticated():
            link = Link.objects.get_or_create(target=target, ip_added=user_ip, 
                                              user_added=request.user)[0]
        else:
            link = Link.objects.get_or_create(target=target, 
                                              ip_added=user_ip)[0]
        return self.success(link=link.pk)


class IncreaseDurationView(AuthenticatedAjaxView):
    pass

