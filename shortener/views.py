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
    pass


class AuthenticatedAjaxView(AjaxView):
    pass
