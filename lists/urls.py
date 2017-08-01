from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^lists/new$', views.new_list, name='new_list'),
    url(r'^lists/(.+)/$', views.view_list, name='view_list'),
]
