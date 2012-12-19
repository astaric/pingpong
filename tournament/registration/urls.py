from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='player_index'),
    url(r'^player/(\d+)/$', views.player_details, name='player_details'),
    url(r'^player/(\d+)/edit$', views.player_edit, name='player_edit'),
)
