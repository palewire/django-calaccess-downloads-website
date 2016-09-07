from bakery.views import BuildableTemplateView


class OfficialDocumentation(BuildableTemplateView):
    """
    Explanation of official CAL-ACCESS documentation.
    """
    build_path = "documentation/calaccess-official-documentation/index.html"
    template_name = "calaccess_website/official_documentation.html"
