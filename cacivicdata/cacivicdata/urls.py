from django.conf.urls import url
from django.contrib import admin
from . import views
from calaccess_raw.models.tracking import RawDataVersion


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.versions_list, name='index'),
    url(r'^versions/$', views.versions_list, name='versions'),
    url(
        r'^versions/(?P<version>[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2})/$',
        views.version,
        name='version'
    ),
    url(r'^latest/$', views.latest_version, name='latest'),
    url(r'^data_files/$', views.data_files_list, name='data_files'),
    url(
        r'^data_files/(?P<file_name>\w+)/$',
        views.data_file,
        name='data_file',
    ),
]
