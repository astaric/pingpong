from django.conf.urls import patterns as urls_patterns, url, include

from . import views

patterns = lambda *urls: urls_patterns('', *urls)

urlpatterns = patterns(
    url(r'^$', views.category_list, name='category_list'),
    url(r'^add/$', views.add_category, name='category_add'),
    url(r'^(?P<category_id>\d+)/', include(patterns(
        url(r'^$', views.category_details, name='category'),
        url(r'^edit/$', views.edit_category, name='edit_category'),
        url(r'^delete/$', views.delete_category, name='category_delete'),

        url(r'^brackets/create/$', views.create_brackets, name='create_brackets'),
        url(r'^brackets/delete/$', views.delete_brackets, name='delete_brackets'),

        url(r'^groups/create/$', views.create_groups, name='create_groups'),
        url(r'^groups/create_ng/$', views.create_groups_ng, name='create_groups_ng'),
        url(r'^groups/delete/', views.delete_groups, name='delete_groups'),

        url(r'^players.json$', views.category_players, name='category_players'),
        url(r'^players/edit/$', views.edit_category_players, name='category_edit_players'),
    ))),
    url(r'^known_clubs/$', views.known_clubs, name="known_clubs"),
    url(r'^known_players/$', views.known_players, name="known_players")
)
