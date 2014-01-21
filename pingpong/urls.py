from django.conf.urls import patterns, include, url

from django.contrib.auth.views import login, logout

from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^category/', include('pingpong.signup.urls')),
    url(r'^dashboard/', include('pingpong.dashboard.urls')),

    url(r'^brackets_slideshow', 'pingpong.slideshow.views.brackets_slideshow', name='brackets_slideshow'),
    url(r'^groups_slideshow', 'pingpong.slideshow.views.groups_slideshow', name='groups_slideshow'),

    url(r'^accounts/login/$', login, name='auth_login', kwargs=dict(template_name='pingpong/login.html')),
    url(r'^accounts/logout/$', logout, name='auth_logout', kwargs=dict(template_name='pingpong/logged_out.html')),

    url(r'^report/$', 'pingpong.printing.views.print_report'),
    url(r'^results/$', 'pingpong.printing.views.print_results'),

    url(r'^admin/', include(admin.site.urls)),
)
