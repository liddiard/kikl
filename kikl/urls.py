from django.conf.urls import patterns, include, url

from shortener import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # front
    url(r'^$', views.FrontPageView.as_view(), name='front'),

    # api
    url(r'^api/link-add/$', views.AddLinkView.as_view(), name='link_add'),
    url(r'^api/link-increaseduration/$', views.IncreaseDurationView.as_view(), 
        name='link_increaseduration'),

    # admin
    url(r'^admin/', include(admin.site.urls)),

    # accounts
    (r'^accounts/', include('kikl.urls_accounts')),

    # main
    url(r'^links/$', views.LinksView.as_view(), name='links'),
    url(r'^(?P<adjective>\S+)-(?P<noun>\S+)/time/$', views.LinkView.as_view(), 
        name='link'),
    url(r'^(?P<adjective>\S+)-(?P<noun>\S+)/$', views.target_view, 
        name='target'),
)
