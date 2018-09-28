from bakery.views import BuildableListView
from calaccess_raw import get_model_list
from calaccess_raw.models import RawDataVersion
from calaccess_raw.annotations import FORMS
from calaccess_website.views.docs.ccdc import get_processed_data_files


class AbstractSitemapView(BuildableListView):
    """
    Abstract base class that will render a generic ListView as XML.
    """
    def render_to_response(self, context):
        return super(AbstractSitemapView, self).render_to_response(
            context,
            content_type='text/xml'
        )


class OtherSitemap(AbstractSitemapView):
    """
    Hodge podge of links we need to add manually to the sitemap.
    """
    build_path = "other-sitemap.xml"
    template_name = "calaccess_website/sitemaps/other-sitemap.xml"
    url_list = [
        "http://calaccess.californiacivicdata.org/downloads/",
        "http://calaccess.californiacivicdata.org/downloads/latest/",
        "http://calaccess.californiacivicdata.org/documentation/",
        "http://calaccess.californiacivicdata.org/documentation/raw-files/",
        "http://calaccess.californiacivicdata.org/documentation/processed-files/",
        "http://calaccess.californiacivicdata.org/documentation/calaccess-forms/",
        "http://calaccess.californiacivicdata.org/documentation/documentation/calaccess-official-documentation/",
        "http://calaccess.californiacivicdata.org/documentation/frequently-asked-questions/",
    ]

    def get_queryset(self):
        return [dict(url=url) for url in self.url_list]


class VersionSitemap(AbstractSitemapView):
    """
    A machine-readable list of all version detail pages.
    """
    build_path = 'downloads-sitemap.xml'
    template_name = 'calaccess_website/sitemaps/version-sitemap.xml'
    queryset = RawDataVersion.objects.complete().exclude(release_datetime__lte='2016-07-27')


class VersionYearSitemap(AbstractSitemapView):
    """
    A machine-readable list of the version year archive pages.
    """
    build_path = "downloads-year-sitemap.xml"
    template_name = "calaccess_website/sitemaps/version-archive-year.xml"
    model = RawDataVersion

    def get_queryset(self):
        return self.model.objects.complete().exclude(
            release_datetime__lte='2016-07-27'
        ).datetimes("release_datetime", "year")


class VersionMonthSitemap(AbstractSitemapView):
    """
    A machine-readable list of the version month archive pages.
    """
    build_path = "downloads-month-sitemap.xml"
    template_name = "calaccess_website/sitemaps/version-archive-month.xml"
    model = RawDataVersion

    def get_queryset(self):
        return self.model.objects.complete().exclude(
            release_datetime__lte='2016-07-27'
        ).datetimes("release_datetime", "month")


class CalAccessFileSitemap(AbstractSitemapView):
    """
    A machine-readable list of all CalAccess file detail pages.
    """
    build_path = 'raw-file-sitemap.xml'
    template_name = 'calaccess_website/sitemaps/calaccess-file-sitemap.xml'
    queryset = get_model_list()


class CcdcFileSitemap(AbstractSitemapView):
    """
    A machine-readable list of all CCDC file detail pages.
    """
    build_path = 'processed-file-sitemap.xml'
    template_name = 'calaccess_website/sitemaps/ccdc-file-sitemap.xml'
    queryset = get_processed_data_files()


class CalAccessFileDownloadsSitemap(AbstractSitemapView):
    """
    A machine-readable list of all CalAccess file archive download pages.
    """
    build_path = 'raw-file-downloads-sitemap.xml'
    template_name = 'calaccess_website/sitemaps/calaccess-file-downloads-sitemap.xml'
    queryset = get_model_list()


class CcdcFileDownloadsSitemap(AbstractSitemapView):
    """
    A machine-readable list of all CCDC file archive download pages.
    """
    build_path = 'processed-file-downloads-sitemap.xml'
    template_name = 'calaccess_website/sitemaps/ccdc-file-downloads-sitemap.xml'
    queryset = get_processed_data_files()


class FormSitemap(AbstractSitemapView):
    """
    A machine-readable list of all form detail pages.
    """
    build_path = 'form-sitemap.xml'
    template_name = 'calaccess_website/sitemaps/form-sitemap.xml'
    queryset = FORMS
