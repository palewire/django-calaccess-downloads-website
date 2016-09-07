def calaccess_website(request):
    """
    Custom context variables for the CAL-ACCESS downloads website.
    """
    return {
        'CALACCESS_WEBSITE_TITLE': 'California Campaign Finance Data Refinery',
        'CALACCESS_WEBSITE_DESCRIPTION': "Download ready-to-use California \
        campaign finance and lobbying data. We've made the data \
        understandable with documentation and examples. Brought to you by the\
        California Civic Data Coalition.",
        'CALACCESS_WEBSITE_DOMAIN': 'calaccess.californiacivicdata.org'
    }
