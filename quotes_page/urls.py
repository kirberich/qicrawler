from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'qi.views.home', name='home'),
    # url(r'^qi/', include('qi.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<quote_id>\d*)$', 'quotes_page.core.views.main', name="main"),
    url(r'^init/?$', 'quotes_page.core.views.init', name="init"),
    url(r'^stats/?$', 'quotes_page.core.views.stats', name="stats"),
)
