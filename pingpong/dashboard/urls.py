from django.conf.urls import patterns as urls_patterns, url

from . import views

patterns = lambda *urls: urls_patterns('', *urls)

urlpatterns = patterns(
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^match/(?P<match_id>\d+)/score/set/$', views.set_score, name='set_score'),
)
