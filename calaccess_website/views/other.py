from calaccess_raw.models.tracking import RawDataVersion
from django.views.generic import ArchiveIndexView, TemplateView


class Home(ArchiveIndexView):
    """
    The site homepage.
    """
    model = RawDataVersion
    date_field = "release_datetime"
    template_name = "calaccess_website/home.html"


class CalAccessRobotsTxt(TemplateView):
    """
    The robots.txt file.
    """
    template_name = "calaccess_website/robots.txt"

    def render_to_response(self, context):
        return super(CalAccessRobotsTxt, self).render_to_response(
            context,
            content_type='text'
        )
