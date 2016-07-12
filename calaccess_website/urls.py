from django.conf.urls import url
from calaccess_website import views, sitemaps


urlpatterns = [
    # The homepage
    url(
        r'^$',
        views.Home.as_view(),
        name="home",
    ),

    # Version archive views
    url(
        r'^versions/$',
        views.VersionArchiveIndex.as_view(),
        name="version_archive_index",
    ),
    url(
        r'^versions/(?P<year>[0-9]{4})/$',
        views.VersionYearArchiveList.as_view(),
        name="version_archive_year"
    ),
    url(
        r'^versions/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/$',
        views.VersionMonthArchiveList.as_view(),
        name="version_archive_month"
    ),
    url(
        r'^versions/latest/$',
        views.LatestVersion.as_view(),
        name='version_latest_redirect'
    ),
    url(
        r'^versions/(?P<year>[0-9]{4})/(?P<month>[0-9]+)/(?P<release_epochtime>[0-9]+)/$',
        views.VersionDetail.as_view(),
        name="version_detail"
    ),

    # File views
    url(
        r'^files/$',
        views.FileList.as_view(),
        name='file_list'
    ),
    url(
        r'^files/(?P<file_name>\w+)/$',
        views.FileDetail.as_view(),
        name='file_detail',
    ),

    # Machine-readable stuff
    url(
        r'^robots.txt$',
        views.CalAccessRobotsTxtView.as_view(),
        name='robots_txt'
    ),
    url(
        r'^file-sitemap.xml$',
        sitemaps.FileSitemapView.as_view(),
        name='file_sitemap'
    ),
    url(
        r'^version-sitemap.xml$',
        sitemaps.VersionSitemapView.as_view(),
        name='version_sitemap'
    ),
    url(
        r'^other-sitemap.xml$',
        sitemaps.OtherSitemapView.as_view(),
        name='other_sitemap'
    ),
]
