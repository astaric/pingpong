from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='groups'),
    url(r'^category/(?P<id>\d+)/add$', views.create_groups, name='groups_create'),
    url(r'^(?P<id>\d+)/edit$', views.edit_group, name='group_edit'),
    url(r'^category/(?P<id>\d+)/delete$', views.delete_groups, name='groups_delete')
)
