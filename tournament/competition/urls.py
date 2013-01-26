from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^category/$', views.category_index, name='category_index'),
    url(r'^category/pairs/$', views.category_index, name='pairs_index', kwargs={'filter': 'pairs'}),
    url(r'^category/(?P<category_id>\d+)/$', views.category_details, name='group_details'),
    url(r'^category/(?P<category_id>\d+)/print$', views.print_group, name='print_group'),
    url(r'^match/upcoming', views.match_index, name='upcoming_matches', kwargs={'filter': 'upcoming'}),
    url(r'^match/current', views.match_index, name='current_matches', kwargs={'filter': 'current'}),
    #url(r'^tables', views.tables, name='tables'),
    url(r'^match/set_table', views.set_table, name='set_table'),
    url(r'^match/clear_table/(?P<table_id>\d+)/', views.clear_table, name='clear_table'),
    url(r'^match/set_scores', views.set_score, name='set_score'),
    url(r'^match/set_places', views.set_places, name='set_places'),
    url(r'^match/set_leaders', views.set_leaders, name='set_leaders'),
    url(r'^match/create_pair_bracket', views.create_pair_bracket, name='create_pair_bracket'),
    url(r'^match/(?P<match_id>\d+)/print', views.print_match, name='print_match'),
    url(r'^slideshow$', views.slide_show, name='slide_show'),
    url(r'^slideshow2$', views.slide_show2, name='slide_show_brackets'),
)
