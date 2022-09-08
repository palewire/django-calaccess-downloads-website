from bakery.views import BuildableTemplateView


class OfficialDocumentation(BuildableTemplateView):
    """
    Explanation of official CAL-ACCESS documentation.
    """
    template_name = "calaccess_website/docs/official/doc_list.html"
    build_path = "documentation/calaccess-official-documentation/index.html"

    def get_context_data(self):
        context = {
            'title': 'CAL-ACCESS official documentation',
            'description': "The jumbled, fragmentary and unreliable documentation \
for the CAL-ACCESS database provided by California's Secretary of State."
        }
        return context
