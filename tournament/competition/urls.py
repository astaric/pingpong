from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='group_index'),
    url(r'^category/(?P<category_id>\d+)/$', views.details, name='group_details'),
    url(r'^upcoming_matches', views.upcoming_matches, name='upcoming_matches'),
    url(r'^(\d+)/print_match.txt', views.print_match, name='print_match'),
)
