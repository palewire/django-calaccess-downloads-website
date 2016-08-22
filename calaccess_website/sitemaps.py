from calaccess_raw import get_model_list
from bakery.views import BuildableListView
from calaccess_raw.models import RawDataVersion
from calaccess_raw.annotations.filing_forms import all_filing_forms


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
    template_name = "calaccess_website/other-sitemap.xml"
    queryset = [
        {"url": "/"},
        {"url": "/forms/"},
        {"url": "/files/"},
        {"url": "/downloads/"},
        {"url": "/downloads/latest/"},
        {"url": "/government-documentation/"},
    ]


class VersionSitemap(AbstractSitemapView):
    """
    A machine-readable list of all version detail pages.
    """
    build_path = 'version-sitemap.xml'
    template_name = 'calaccess_website/version-sitemap.xml'
    queryset = RawDataVersion.objects.complete()


class VersionYearSitemap(AbstractSitemapView):
    """
    A machine-readable list of the version year archive pages.
    """
    build_path = "version-archive-year.xml"
    template_name = "calaccess_website/version-archive-year.xml"
    model = RawDataVersion

    def get_queryset(self):
        return self.model.objects.complete().datetimes("release_datetime", "year")


class VersionMonthSitemap(AbstractSitemapView):
    """
    A machine-readable list of the version month archive pages.
    """
    build_path = "version-archive-month.xml"
    template_name = "calaccess_website/version-archive-month.xml"
    model = RawDataVersion

    def get_queryset(self):
        return self.model.objects.complete().datetimes("release_datetime", "month")


class FileSitemap(AbstractSitemapView):
    """
    A machine-readable list of all file detail pages.
    """
    build_path = 'file-sitemap.xml'
    template_name = 'calaccess_website/file-sitemap.xml'
    queryset = get_model_list()


class FileDownloadsSitemap(AbstractSitemapView):
    """
    A machine-readable list of all file archive download pages.
    """
    build_path = 'file-downloads-sitemap.xml'
    template_name = 'calaccess_website/file-downloads-sitemap.xml'
    queryset = get_model_list()


class FormSitemap(AbstractSitemapView):
    """
    A machine-readable list of all form detail pages.
    """
    build_path = 'file-sitemap.xml'
    template_name = 'calaccess_website/form-sitemap.xml'
    queryset = all_filing_forms
