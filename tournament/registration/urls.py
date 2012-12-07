from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='player_index'),
    url(r'^(\d+)/$', views.details, name='player_details'),
)
