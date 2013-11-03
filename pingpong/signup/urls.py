from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='signup'),
    url(r'^(?P<id>\d+)/(?P<name>[^/]*)/$', views.edit_category, name='signup_category')
)
