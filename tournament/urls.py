from django.conf.urls import patterns, include, url

from .registration import urls as player_urls
from .competition import urls as competition_urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include(competition_urls)),
    #url(r'^registration/', include(player_urls)),
    #url(r'^competition/', include(competition_urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
