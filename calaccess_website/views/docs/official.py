from django.views.generic.base import TemplateView


class OfficialDocumentation(TemplateView):
    """
    Explanation of official CAL-ACCESS documentation.
    """
    template_name = "calaccess_website/docs/official/doc_list.html"

    def get_context_data(self):
        context = {
            'title': 'CAL-ACCESS official documentation',
            'description': "The jumbled, fragmentary and unreliable documentation \
for the CAL-ACCESS database provided by California's Secretary of State."
        }
        return context
