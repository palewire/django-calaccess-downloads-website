from bakery.views import BuildableTemplateView


class DocumentationIndex(BuildableTemplateView):
    """
    An index page for linking to all of our documentation sections
    """
    build_path = "documentation/index.html"
    template_name = "calaccess_website/documentation_index.html"

    def get_context_data(self):
        object_list = [
            dict(
                name='Raw CAL-ACCESS files',
                description="Definitions, record layouts and data dictionaries for the {} \
database ",
                url=""
            ),
            dict(
                name='CAL-ACCESS forms',
                description="",
                url=""
            ),
            dict(
                name='Technical documentation',
                description="",
                url=""
            ),
            dict(
                name='References',
                description="",
                url=""
            ),
        ]
        return {
            'object_list': object_list
        }
