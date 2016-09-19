from calaccess_raw.models.tracking import RawDataVersion
from bakery.views import BuildableArchiveIndexView, Buildable404View, BuildableRedirectView


class Home(BuildableArchiveIndexView):
    """
    The site homepage.
    """
    model = RawDataVersion
    date_field = "release_datetime"
    build_path = "index.html"
    template_name = "calaccess_website/home.html"


class HomeRedirect(BuildableRedirectView):
    build_path = "index.html"
    url = "http://www.californiacivicdata.org/"


class CalAccess404View(Buildable404View):
    """
    The 404 page.
    """
    build_path = "404.html"
    template_name = "calaccess_website/404.html"


class CalAccessRobotsTxt(Buildable404View):
    """
    The robots.txt file.
    """
    build_path = "robots.txt"
    template_name = "calaccess_website/robots.txt"

    def render_to_response(self, context):
        return super(CalAccessRobotsTxt, self).render_to_response(
            context,
            content_type='text'
        )
