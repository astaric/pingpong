from django.conf.urls import patterns, include, url

from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pingpong.views.home', name='home'),
    url(r'', include('pingpong.signup.urls')),
    url(r'', include('pingpong.group.urls')),

    url(r'^brackets_slideshow', 'pingpong.slideshow.views.brackets_slideshow', name='brackets_slideshow'),
    url(r'^groups_slideshow', 'pingpong.slideshow.views.groups_slideshow', name='groups_slideshow'),

    url(r'^live/upcoming', 'pingpong.live.views.upcoming_matches', name='upcoming_matches'),
    url(r'^live/current', 'pingpong.live.views.current_matches', name='current_matches'),

    url(r'^accounts/login/$', login, name='auth_login'),
    url(r'^accounts/logout/$', logout, name='auth_logout'),

    url(r'^report/$', 'pingpong.printing.views.print_report'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
