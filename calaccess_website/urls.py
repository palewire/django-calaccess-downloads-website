from django.conf.urls import url
from calaccess_website import views


urlpatterns = [
    url(r'^$', views.VersionList.as_view()),
    url(r'^versions/$', views.VersionList.as_view()),
    url(
        r'^versions/(?P<version>[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2})/$',
        views.VersionDetail.as_view()
    ),
    url(r'^latest/$', views.LatestVersion.as_view(), name='latest'),
    url(
        r'^raw_data_files/$',
        views.RawDataFileList.as_view(),
        name='raw_data_files'
    ),
    url(
        r'^raw_data_files/(?P<file_name>\w+)/$',
        views.RawDataFileDetail.as_view(),
        name='raw_data_file',
    ),
]
