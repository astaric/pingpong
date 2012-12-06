from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='group_index'),
    url(r'^(\d+)/$', views.details, name='group_details'),
    url(r'^(\d+)/print_match.txt', views.print_match, name='print_match'),
)
