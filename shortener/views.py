import json
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from shortener import models


class FrontPageView(TemplateView):
    
    template_name = "front.html"
