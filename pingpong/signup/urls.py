from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^signup/$', views.index, name='signup'),
    url(r'^category/add$', views.add_category, name='category_add'),
    url(r'^category/(?P<category_id>\d+)/$', views.category_details, name='category'),
    url(r'^category/(?P<category_id>\d+)/edit/$', views.edit_category, name='category_edit'),
    url(r'^category/(?P<category_id>\d+)/players/edit/$', views.edit_category_players, name='category_edit_players'),
    url(r'^category/(?P<category_id>\d+)/delete$', views.delete_category, name='category_delete'),
    url(r'^category/(?P<category_id>\d+)/delete_groups$', views.delete_groups, name='delete_groups'),
    url(r'^category/(?P<category_id>\d+)/delete_brackets$', views.delete_brackets, name='delete_brackets'),
)
