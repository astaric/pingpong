from django.conf.urls import patterns as urls_patterns, url

from . import views

patterns = lambda *urls: urls_patterns('', *urls)

urlpatterns = patterns(
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^match/(?P<match_id>\d+)/score/set/$', views.set_score, name='set_score'),
    url(r'^match/(?P<match_id>\d+)/table/clear/$', views.clear_table, name='clear_table'),

    url(r'^match/upcoming/$', views.upcoming_matches),
    url(r'^match/(?P<match_id>\d+)/details/$', views.match_details),
    url(r'^tables/$', views.tables),
)
