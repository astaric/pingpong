from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^groups/$', views.index, name='groups_index'),

    url(r'^category/(?P<category_id>\d+)/groups$', views.GroupsView.as_view(), name='groups'),
    url(r'^category/(?P<category_id>\d+)/groups?/(?P<group_id>\d+)', views.edit_group, name='edit_group'),
)
