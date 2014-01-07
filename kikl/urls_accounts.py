from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from kikl.accounts.views import RegistrationView
from kikl.accounts.forms import UserRegistrationForm

urlpatterns = patterns('',

    # override the default urls
    url(r'^password/change/$',
                auth_views.password_change,
                name='password_change'),
    url(r'^password/change/done/$',
                auth_views.password_change_done,
                name='password_change_done'),
    url(r'^password/reset/$',
                auth_views.password_reset,
                name='password_reset'),
    url(r'^password/reset/done/$',
                auth_views.password_reset_done,
                name='password_reset_done'),
    url(r'^password/reset/complete/$',
                auth_views.password_reset_complete,
                name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                auth_views.password_reset_confirm,
                name='password_reset_confirm'),

    # customize user registration form
    url(r'^register/$', RegistrationView.as_view(),
        name='registration_register'
    ),

    # and now add the registration urls
    url(r'', include('registration.backends.default.urls')),
)
