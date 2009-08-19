from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', include('force_quared.historilator.urls')),
	#(r'^login/', 'force_quared.historilator.views.login'),
	(r'^login/', 'django.views.generic.simple.direct_to_template', {'template':'login.html'}),
	(r'^test/', 'django.views.generic.simple.direct_to_template', {'template':'test.html'}),
	(r'^addServices/', 'force_quared.historilator.views.addServices'),
	(r'^auth/', 'force_quared.historilator.views.auth'),
	(r'^authorizeSource/', 'force_quared.historilator.views.authorizeSource'),
	(r'^accounts/login/', 'django.views.generic.simple.direct_to_template', {'template':'login.html'}),
	(r'^register/', 'force_quared.historilator.views.register'),
    (r'^force_quared/', include('force_quared.historilator.urls')),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/rodericj/webapps/force_quared/force_quared/media'}),

    #(r'^$/', include('force_quared.historilator.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
