def calaccess_website(request):
    """
    Custom context variables for the CAL-ACCESS downloads website.
    """
    return {
        'CALACCESS_WEBSITE_TITLE': 'The CAL-ACCESS archive',
        'CALACCESS_WEBSITE_DESCRIPTION': "Daily snapshots of campaign finance \
and lobbying disclosure data from California",
    }
