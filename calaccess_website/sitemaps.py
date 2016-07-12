from calaccess_raw import get_model_list
from bakery.views import BuildableListView
from calaccess_raw.models import RawDataVersion


class AbstractSitemapClass(BuildableListView):
    def render_to_response(self, context):
        return super(AbstractSitemapClass, self).render_to_response(
            context,
            content_type='text/xml'
        )


class OtherSitemapView(AbstractSitemapClass):
    build_path = "other-sitemap.xml"
    template_name = "calaccess_website/other-sitemap.xml"
    queryset = [
        {"url": "/"},
        {"url": "/files/"},
        {"url": "/versions/"},
        {"url": "/versions/latest/"},
    ]


class VersionSitemapView(AbstractSitemapClass):
    """
    A list of all graphics in a Sitemap ready for Google.
    """
    build_path = 'version-sitemap.xml'
    template_name = 'calaccess_website/version-sitemap.xml'
    model = RawDataVersion


class FileSitemapView(AbstractSitemapClass):
    """
    A list of all graphics in a Sitemap ready for Google.
    """
    build_path = 'file-sitemap.xml'
    template_name = 'calaccess_website/file-sitemap.xml'
    queryset = get_model_list()
