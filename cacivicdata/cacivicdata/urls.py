from django.conf.urls import url
from django.contrib import admin
from . import views
from calaccess_raw.models.tracking import RawDataVersion


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.VersionList.as_view()),
    url(r'^versions/$', views.VersionList.as_view()),
    url(
        r'^versions/(?P<version>[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2})/$',
        views.VersionDetail.as_view()
    ),
    url(r'^latest/$', views.LatestVersion.as_view(), name='latest'),
    url(r'^data_files/$', views.DataFileList.as_view(), name='data_files'),
    url(
        r'^data_files/(?P<file_name>\w+)/$',
        views.data_file,
        name='data_file',
    ),
]
