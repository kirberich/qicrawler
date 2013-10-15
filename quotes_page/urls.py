from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'quotes_page.core.views.main', name="main"),
    url(r'^(?P<quote_id>\d+)/?$', 'quotes_page.core.views.quote', name="quote"),
    #url(r'^init/?$', 'quotes_page.core.views.init', name="init"),
    url(r'^stats/?$', 'quotes_page.core.views.stats', name="stats"),
    (r'^login/?$', 'quotes_page.core.views.login_view'),
    (r'^logout/?$', 'quotes_page.core.views.logout_view'),
    (r'^quote_edit/(?P<quote_id>\d+)/?$', 'quotes_page.core.views.quote_edit'),
    (r'^quote_delete/(?P<quote_id>\d+)/?$', 'quotes_page.core.views.quote_delete'),    
)
