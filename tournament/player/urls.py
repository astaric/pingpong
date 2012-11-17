from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
   url(r'^$', views.list, name='list_players'),
   url(r'^(\d+)/', views.show, name='show_player'),
)
