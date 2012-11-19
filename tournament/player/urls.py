from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
   url(r'^$', views.index, name='player_index'),
   url(r'^(\d+)/$', views.details, name='player_details'),
   url(r'^(\d+)/print_match.txt', views.print_match, name='print_match'),
)
