from django.conf.urls import url
from calaccess_website import views


urlpatterns = [
    # The homepage
    url(
        r'^$',
        views.VersionArchiveIndex.as_view(),
        name="version_index",
    ),

    # Version archive views
    url(
        r'^archive/(?P<year>[0-9]{4})/$',
        views.VersionYearArchiveList.as_view(),
        name="version_year_archive"
    ),
    url(
        r'^versions/(?P<pk>[0-9]{1,})/$',
        views.VersionDetail.as_view(),
        name="version_detail"
    ),
    url(
        r'^versions/latest/$',
        views.LatestVersion.as_view(),
        name='version_latest_redirect'
    ),

    # Raw data file archive views
    url(
        r'^raw-data-files/$',
        views.RawDataFileList.as_view(),
        name='rawdatafiles_list'
    ),
    url(
        r'^raw-data-files/(?P<file_name>\w+)/$',
        views.RawDataFileDetail.as_view(),
        name='rawdatafile_detail',
    ),
]
