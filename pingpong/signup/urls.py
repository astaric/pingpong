from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='signup'),
    url(r'^category/add$', views.add_category, name='category_add'),
    url(r'^category/(?P<id>\d+)/$', views.edit_category, name='category_edit'),
    url(r'^category/(?P<id>\d+)/delete$', views.delete_category, name='category_delete')
)
