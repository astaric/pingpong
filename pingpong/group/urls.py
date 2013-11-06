from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^groups/$', views.index, name='groups'),
    url(r'^category/(?P<category_id>\d+)/groups$', views.list_groups, name='groups_list'),
    url(r'^category/(?P<category_id>\d+)/groups/add$', views.create_groups, name='groups_create'),
    url(r'^group/(?P<group_id>\d+)/edit$', views.edit_group, name='group_edit'),
    url(r'^category/(?P<category_id>\d+)/groups/delete$', views.delete_groups, name='groups_delete')
)
