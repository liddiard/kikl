import json
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from shortener import models


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
    pass


class IncreaseDurationView(AuthenticatedAjaxView):
    pass

