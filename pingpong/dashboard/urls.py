from django.conf.urls import patterns as urls_patterns, url

from . import views

patterns = lambda *urls: urls_patterns('', *urls)

urlpatterns = patterns(
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^match/(?P<match_id>\d+)/score/set/$', views.set_score, name='set_score'),
    url(r'^match/(?P<match_id>\d+)/table/clear/$', views.clear_table, name='clear_table'),
    url(r'^match/(?P<match_id>\d+)/table/set/$', views.set_table, name='set_table'),
    url(r'^group/(?P<group_id>\d+)/score/set/$', views.set_group_scores, name='set_group_scores'),
    url(r'^match/history/$', views.match_history, name="match_history"),

    url(r'^match/upcoming/$', views.upcoming_matches),

    url(r'^match/(?P<match_id>\d+)/details/$', views.match_details),
    url(r'^tables/$', views.tables),
)
