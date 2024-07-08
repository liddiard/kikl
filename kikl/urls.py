from django.urls import include, path
from django.contrib import admin

from shortener import views

urlpatterns = [
    path('', views.FrontPageView.as_view(), name='front'),
    path('api/link/', views.LinkView.as_view(), name='link'),
    path('admin/', admin.site.urls),
    path('<str:adjective>-<str:noun>/', views.target_view, 
         name='target'),
]
