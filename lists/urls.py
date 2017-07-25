from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^lists/new$', views.new_list, name='new_list'),
    url(r'^the-only-list-in-the-world/$', views.view_list, name='view_list'),
]
