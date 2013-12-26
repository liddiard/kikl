from django.conf.urls import patterns, include, url

from shortener import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.FrontPageView.as_view(), name='front'),

    # api
    url(r'^api/link-add/$', views.AddLinkView.as_view(), name='link_add'),

    # admin
    url(r'^admin/', include(admin.site.urls)),
)
