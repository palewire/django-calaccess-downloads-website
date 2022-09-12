from django.urls import re_path
from calaccess_website import views, sitemaps
from django.views.generic.base import RedirectView


urlpatterns = [
    # The homepage
    re_path(
        r'^$',
        RedirectView.as_view(url='https://www.californiacivicdata.org/'),
        name="home",
    ),

    #
    # Downloads
    #

    re_path(
        r'^downloads/latest/$',
        views.LatestVersion.as_view(),
        name='version_latest'
    ),

    #
    # Documentation
    #

    # Index
    re_path(
        r'^documentation/$',
        views.DocumentationIndex.as_view(),
        name='docs_index'
    ),

    # CAL-ACCESS file views
    re_path(
        r'^documentation/raw-files/$',
        views.CalAccessFileList.as_view(),
        name='calaccess_file_list'
    ),
    re_path(
        r'^documentation/raw-files/(?P<slug>[-\w]+)/$',
        views.CalAccessFileDetail.as_view(),
        name='calaccess_file_detail',
    ),
    re_path(
        r'^documentation/raw-files/(?P<slug>[-\w]+)/downloads/$',
        views.CalAccessFileDownloadsList.as_view(),
        name='calaccess_file_downloads_list',
    ),

    # CCDC file views
    re_path(
        r'^documentation/processed-files/$',
        views.CcdcFileList.as_view(),
        name='ccdc_file_list'
    ),
    re_path(
        r'^documentation/processed-files/(?P<slug>[-\w]+)/$',
        views.CcdcFileDetail.as_view(),
        name='ccdc_file_detail',
    ),
    re_path(
        r'^documentation/processed-files/(?P<slug>[-\w]+)/downloads/$',
        views.CcdcFileDownloadsList.as_view(),
        name='ccdc_file_downloads_list',
    ),

    # Form views
    re_path(
        r'^documentation/calaccess-forms/$',
        views.FormList.as_view(),
        name='form_list'
    ),
    re_path(
        r'^documentation/calaccess-forms/(?P<id>\w+)/$',
        views.FormDetail.as_view(),
        name='form_detail',
    ),

    # Official documentation
    re_path(
        r'^documentation/calaccess-official-documentation/$',
        views.OfficialDocumentation.as_view(),
        name='official_documentation'
    ),

    # Frequently asked questions
    re_path(
        r'^documentation/frequently-asked-questions/$',
        views.FAQ.as_view(),
        name='faq'
    ),

    #
    # Machine-readable stuff
    #

    re_path(
        r'^robots.txt$',
        views.CalAccessRobotsTxt.as_view(),
        name='robots_txt'
    ),
    re_path(
        r'^raw-file-sitemap.xml$',
        sitemaps.CalAccessFileSitemap.as_view(),
        name='calaccess_file_sitemap'
    ),
    re_path(
        r'^raw-file-downloads-sitemap.xml$',
        sitemaps.CalAccessFileDownloadsSitemap.as_view(),
        name='calaccess_file_downloads_sitemap'
    ),
    re_path(
        r'^processed-file-sitemap.xml$',
        sitemaps.CcdcFileSitemap.as_view(),
        name='ccdc_file_sitemap'
    ),
    re_path(
        r'^processed-file-downloads-sitemap.xml$',
        sitemaps.CcdcFileDownloadsSitemap.as_view(),
        name='ccdc_file_downloads_sitemap'
    ),
    re_path(
        r'^form-sitemap.xml$',
        sitemaps.FormSitemap.as_view(),
        name='form_sitemap'
    ),
    re_path(
        r'^other-sitemap.xml$',
        sitemaps.OtherSitemap.as_view(),
        name='other_sitemap'
    ),
]
