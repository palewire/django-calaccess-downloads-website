from calaccess_raw import get_model_list
from bakery.views import BuildableListView
from calaccess_raw.models import RawDataVersion


class VersionSitemapView(BuildableListView):
    """
    A list of all graphics in a Sitemap ready for Google.
    """
    build_path = 'version-sitemap.xml'
    template_name = 'calaccess_website/version-sitemap.xml'
    model = RawDataVersion

    def render_to_response(self, context):
        return super(VersionSitemapView, self).render_to_response(
            context,
            content_type='text/xml'
        )


class FileSitemapView(BuildableListView):
    """
    A list of all graphics in a Sitemap ready for Google.
    """
    build_path = 'file-sitemap.xml'
    template_name = 'calaccess_website/file-sitemap.xml'
    queryset = get_model_list()

    def render_to_response(self, context):
        return super(FileSitemapView, self).render_to_response(
            context,
            content_type='text/xml'
        )
