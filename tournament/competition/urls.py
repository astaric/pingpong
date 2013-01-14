from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='group_index'),
    url(r'^category/(?P<category_id>\d+)/$', views.details, name='group_details'),
    url(r'^matches/upcoming', views.match_index, name='upcoming_matches', kwargs={'filter': 'upcoming'}),
    url(r'^matches/current', views.match_index, name='current_matches', kwargs={'filter': 'current'}),
    url(r'^tables', views.tables, name='tables'),
    url(r'^match/set_table', views.set_table, name='set_table'),
    url(r'^match/set_scores', views.set_score, name='set_score'),
    url(r'^match/(?P<match_id>\d+)/', views.match_details, name='match_details'),
    url(r'^(\d+)/print_match.txt', views.print_match, name='print_match'),
)
