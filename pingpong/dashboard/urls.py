from django.conf.urls import patterns as urls_patterns, url

from . import views

patterns = lambda *urls: urls_patterns('', *urls)

urlpatterns = patterns(
    url(r'^$', views.dashboard, name='upcoming_matches'),
    url(r'^tableinfo/(?P<table_id>\d+)/', 'pingpong.dashboard.views.set_score', name='set_score'),
)
