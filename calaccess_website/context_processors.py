def calaccess_website(request):
    """
    Custom context variables for the CAL-ACCESS downloads website.
    """
    return {
        'CALACCESS_WEBSITE_TITLE': 'California campaign data',
        'CALACCESS_WEBSITE_DESCRIPTION': "Download campaign finance and lobbying disclosure data from \
the California Secretary of State's CAL-ACCESS database ",
        'CALACCESS_WEBSITE_DOMAIN': 'calaccess.californiacivicdata.org'
    }
